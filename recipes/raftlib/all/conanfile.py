from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeDeps, CMakeToolchain, CMake
from conan.tools.scm import Git
from conan.tools.build import check_min_cppstd

class RaftlibConan(ConanFile):
    name = "raftlib"
    description = "streaming/dataflow concurrency via C++ iostream-like operators"
    license = "Apache-2.0"
    homepage = "https://github.com/RaftLib/RaftLib"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared" : [True, False]}
    default_options = {"shared" : False}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate_build(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def source(self):
        git = Git(self)
        git.clone(url=self.homepage, target=self.source_folder)
        git.checkout(f"v{self.version}")
        git.run("submodule update --init --recursive")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()
