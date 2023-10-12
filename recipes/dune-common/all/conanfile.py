from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, collect_libs

class dune_commonRecipe(ConanFile):
    name = "dune-common"
    package_type = "library"

    # Optional metadata
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of dune-common package here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def build_requirements(self):
        self.requires("vc/1.4.2")
        self.requires("openblas/0.3.20")
        self.requires("onetbb/2021.10.0")
        self.requires("metis/5.2.1")

        self.requires("gmp/6.3.0")
        

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("metis", "cmake_find_mode", "module")
        deps.set_property("metis", "cmake_file_name", "METIS")
        deps.set_property("metis", "cmake_target_name", "METIS::METIS")
        deps.set_property("gmp", "cmake_find_mode", "module")
        deps.set_property("gmp", "cmake_file_name", "GMP")
        deps.set_property("gmp", "cmake_target_name", "GMP::gmpxx")
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["DUNE_ENABLE_PYTHONBINDINGS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.defines = ["ENABLE_TBB=1"]
        #Note No namespace
        self.cpp_info.set_property("cmake_target_name", "dune-common")
        
