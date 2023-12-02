from conan import ConanFile
from conan.tools.files import get
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd

class azmqConan(ConanFile):
    name = "azmq"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zeromq/azmq"
    license = "BSL-1.0"
    settings =  "compiler", "build_type"
    requires = ("boost/1.83.0", "zeromq/4.3.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")
        
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["AZMQ_NO_TESTS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def package(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.install()

    def package_id(self):
        self.info.clear()

    
