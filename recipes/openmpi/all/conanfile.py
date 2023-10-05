from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, mkdir, rmdir
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
#from conans import ConanFile, tools, AutoToolsBuildEnvironment
#from conans.errors import ConanInvalidConfiguration
import os
from pathlib import Path

required_conan_version = ">=1.29.1"


class OpenMPIConan(ConanFile):
    name = "openmpi"
    homepage = "https://www.open-mpi.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "mpi", "openmpi")
    description = "A High Performance Message Passing Library"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fortran": ["yes", "mpifh", "usempi", "usempi80", "no"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fortran": "no"
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def layout(self):
        basic_layout(self, src_folder="src")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("OpenMPI doesn't support Windows")

    def requirements(self):
        # FIXME : self.requires("libevent/2.1.12") - try to use libevent from conan
        self.requires("zlib/1.3")

    def build_requirements(self):
        self.tool_requires("autoconf/2.71")
        self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = AutotoolsDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)
        tc.generate()

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        args = ["--disable-wrapper-rpath", "--disable-wrapper-runpath"]
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")

        #NOTE: handled by conan2
        # if self.options.shared:
        #     args.extend(["--enable-shared", "--disable-static"])
        # else:
        #     args.extend(["--enable-static", "--disable-shared"])
        args.append("--with-pic" if self.options.get_safe("fPIC", True) else "--without-pic")
        args.append("--enable-mpi-fortran={}".format(str(self.options.fortran)))
        args.append("--with-zlib={}".format(self.deps_cpp_info["zlib"].rootpath))
        args.append("--with-zlib-libdir={}".format(self.deps_cpp_info["zlib"].lib_paths[0]))

        #args.append("--datarootdir=${prefix}/res") handled auto by conan2
        self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        at = Autotools(self)
#        at.autoreconf()
        at.configure()
        at.make()


    def package(self):
        at = Autotools(self)
        at.install()
        copy(self, pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        pf = Path(self.package_folder)
        rmdir(pf / "lib" / "pkgconfig")
        rmdir(pf / "share")
        rmdir(pf / "etc")

        #TODO: WTF?
#        remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ['mpi', 'open-rte', 'open-pal']
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread", "rt", "util"]

        self.output.info("Creating MPI_HOME environment variable: {}".format(self.package_folder))
        self.env_info.MPI_HOME = self.package_folder
        self.output.info("Creating OPAL_PREFIX environment variable: {}".format(self.package_folder))
        self.env_info.OPAL_PREFIX = self.package_folder
        mpi_bin = os.path.join(self.package_folder, 'bin')
        self.output.info("Creating MPI_BIN environment variable: {}".format(mpi_bin))
        self.env_info.MPI_BIN = mpi_bin
        self.output.info("Appending PATH environment variable: {}".format(mpi_bin))
        self.env_info.PATH.append(mpi_bin)
