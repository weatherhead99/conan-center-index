from conan import ConanFile
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
import pathlib

class VTKConan(ConanFile):
    name = "vtk"
    homepage = "https://vtk.org"
    description = "The Visualization Toolkit (VTK) is an open-source, freely available software system for 3D computer graphics, modeling, image processing, volume rendering, scientific visualization, and 2D plotting. "
    settings = "os", "arch", "compiler", "build_type"

    requires = ("opengl/system")
    options = { "shared" : [True, False],
                "smp_type" : ["Sequential", "STDThread", "OpenMP", "TBB"]}
    default_options = {"shared" : False,
                       "smp_type" : "STDThread"}

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")


    def requirements(self):
        self.requires("fast_float/[>=3.9 <4]")
        self.requires("exprtk/0.0.2")
        self.requires("pugixml/1.13")
        self.requires("libpng/[>=1.6.37]")
        self.requires("freetype/2.13.0")
        self.requires("libtiff/4.5.1") #NOTE: forced by proj
        self.requires("eigen/[^3.3.9]")
        self.requires("double-conversion/3.3.0")
        self.requires("lz4/1.9.4")
        self.requires("glew/2.2.0")
        self.requires("ogg/1.3.5")
        self.requires("theora/1.1.1")
        self.requires("netcdf/4.8.1")
        self.requires("nlohmann_json/3.11.2")
        self.requires("proj/9.2.1")
        self.requires("jsoncpp/1.9.5")
        self.requires("libxml2/2.11.4")
        self.requires("expat/2.5.0")
        self.requires("icu/73.2")
        self.requires("cgns/4.3.0")
        self.requires("libharu/2.4.3")
        self.requires("fmt/[~9]")

        #conditional requires
        if self.options.smp_type == "TBB":
            self.requires("onetbb/2021.10.0")

        #NOTE: the current proj and netCDF recipes conflict with each other.
        #it appears to be cheaper to rebuild netCDF than proj, so we choose the
        #libcurl and sqlite3 that proj wants (which is newer anyway) and compatibility should be
        #fine with netCDF rebuild. Given that we are going to have to rebuild netCDF anyway,
        #then we might as well bump the HDF5 version that it is otherwise limiting
        self.requires("libcurl/8.2.1", override=True)


        #sqlite3 binary required to build, but also required to link into module
        sqlitestr: str = "sqlite3/3.42.0"
        self.requires(sqlitestr, build=True, run=True)
        self.requires(sqlitestr, headers=True, libs=True)
        self.requires("hdf5/1.14.1", force=True) #NOTE: current netCDF dependency uses 1.14.0

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["VTK_USE_EXTERNAL"] = True
        tc.cache_variables["VTK_LEGACY_REMOVE"] = True
        tc.cache_variables["VTK_SMP_IMPLEMENTATION_TYPE"] = self.options.smp_type

        #deps that aren't found and appear to have no conan packages at the moment
        internal_mods = ["verdict", "pegtl", "ioss", "gl2ps"]

        #deps that are in conan center but of inappropriate versions (need recipe updates)
        internal_mods += ["utf8"] # nearest is utf8.h/cci.20210310
        
        for mod in internal_mods:
            tc.cache_variables[f"VTK_MODULE_USE_EXTERNAL_VTK_{mod}"] = False



        deps = CMakeDeps(self)
        deps.set_property("libharu", "cmake_target_name", "LibHaru::LibHaru")
        deps.set_property("expat", "cmake_file_name", "EXPAT")
        deps.set_property("expat", "cmake_target_name", "EXPAT::EXPAT")

        deps.set_property("eigen", "cmake_target_name", "Eigen3::Eigen3")
        deps.set_property("lz4", "cmake_target_name", "LZ4::LZ4")


        #NOTE: there is an incompatibility between the include directory base in the
        #double-conversion conan recipe and the CMake find module
        #used by VTK when doubhle-conversion is in external mode. One way round this
        #is to allow use of VTK's internal find module for double-conversion, by correctly setting
        #double-conversion_ROOT
        deps.set_property("double-conversion", "cmake_find_mode", "none")
        dcincl = self.dependencies["double-conversion"].cpp_info.includedirs[0]
        dcroot = str(pathlib.Path(dcincl).parents[0])
        self.output.info(f"dc_include_dir: {dcincl}")
        self.output.info(f"dc_root_dir: {dcroot}")
        tc.cache_variables["double-conversion_ROOT"] = dcroot

        deps.set_property("theora::theora", "cmake_target_name", "THEORA::THEORA")
        if self.settings.os != "Windows" or self.settings.os.subsystem in ["msys", "msys2"]:
            deps.set_property("theora::theoradec", "cmake_target_name", "THEORA::DEC")
            deps.set_property("theora::theoraenc", "cmake_target_name", "THEORA::ENC")

        tc.generate()            
        deps.generate()

    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()
