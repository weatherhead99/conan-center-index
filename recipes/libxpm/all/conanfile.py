import os
import glob

from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.gnu import AutotoolsToolchain, PkgConfigDeps, Autotools, AutotoolsDeps, PkgConfig
from conan.tools.files import get
import shutil


required_conan_version = ">=1.43.0"

def find_file(conanfile, base_path: str, filename: str, return_dir: bool=False):
    for root, dirs, fls in os.walk(base_path):
        if filename in fls:
            pth = os.path.join(root, filename)
            conanfile.output.info(f"found file {filename} at path: {pth}")
            if return_dir:
                return root
            return pth
    else:
        raise FileNotFoundError(f"cannot find file {filename} under directory {base_path}")
            
def find_all_dirs_containing(conanfile, base_path: str, glob: str):
    dirs = set()
    for path in glob.iglob("**/*.pc", recursive=True):
        dirpath = os.path.join(base_path,os.path.split(path)[0])
        dirs.add(dirpath)
    return list(dirs)


class LibXpmConan(ConanFile):
    name = "libxpm"
    description = "X Pixmap (XPM) image file format library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/xorg/lib/libxpm"
    topics = "xpm"
    license = "MIT-open-group"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
#    generators = "CMakeToolchain"
    exports_sources = "CMakeLists.txt", "windows/*"
    no_copy_source = True
    generators = "VirtualBuildEnv", "PkgConfigDeps", "AutotoolsDeps"

    def layout(self):
        basic_layout(self, src_folder="src")
#        cmake_layout(self, src_folder="src")
    
    def validate(self):
        if self.settings.os not in ("Windows", "Linux", "FreeBSD"):
            raise ConanInvalidConfiguration(
                "libXpm is supported only on Windows, Linux and FreeBSD"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        #NOTE: these seem pretty uncontroversial...
        self.tool_requires("autoconf/2.71")
        self.tool_requires("m4/1.4.19")
        self.tool_requires("make/4.3")

        #NOTE: BUT - the two below break the build on e.g. openSUSE Leap,
        # because conan shipped automake cannot get hold of 
        self.tool_requires("pkgconf/1.9.5")
        self.tool_requires("libtool/2.4.7")
        self.tool_requires("automake/1.16.5")
        
        
    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("xorg/system")

        
    def generate(self):
        tc = AutotoolsToolchain(self)
        env = tc.environment()

        #on linux, need to find where the xorg-macros M4 file is
        #(this will be provided by the install of xorg/system)
        #then we let autoreconf know where it is
        #we also need to copy it out somewhere, because otherwise autoreconf will
        #wend up pulling in all the system included M4 files, including libtool.m4 which might be
        #generated with mismatched libtool versions
        if self.settings.os == "Linux":
            xorg_macros_path = find_file(self, "/usr", "xorg-macros.m4")

            extra_m4_path = os.path.join(self.generators_folder, "system_m4")
            self.output.info(f"extra m4 path: {extra_m4_path}")
            os.makedirs(extra_m4_path, exist_ok=True)
            shutil.copyfile(xorg_macros_path,
                            os.path.join(extra_m4_path, "xorg-macros.m4"))

            
            tc.autoreconf_args.append(f"-I{extra_m4_path}")
            self.run(f"autoupdate {extra_m4_path} -I${{AC_MACRODIR}}")

            #we're not even done yet. The build system here will ask for the "xproto" pkg_config
            #package on _some_ linux systems. That's not included in the xorg/system package, presumably
            #because it doesn't always appear in every distro

            pkgconf = PkgConfig(self, "xorg-macros")
            self.output.info(list(pkgconf.variables.items()))

            pkgconf = PkgConfig(self, "xproto")
            self.output.info(list(pkgconf.variables.items()))

            
     
        tc.generate(env)


            
    def build(self):
        acpath = os.path.join(self.source_folder, "configure.ac")
        #NOTE AC_MACRODIR provided by the VirtualBuildEnv here, that's
        #why we need it

        output =  self.run("echo ${PKG_CONFIG_PATH}", env="conanautotoolstoolchain")
        print(output)
                
        self.run(f"autoupdate {acpath} -I ${{AC_MACRODIR}}")
        
        autotools = Autotools(self)
#        autotools.autoreconf(args=["-I/usr/share/aclocal/"])
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        self.copy("COPYING", "licenses")
        self.copy("COPYRIGHT", "licenses")
        self._configure_cmake().install()

    def package_info(self):
        self.cpp_info.libs = ["Xpm"]
        if self.settings.os == "Windows":
            self.cpp_info.defines = ["FOR_MSW"]
