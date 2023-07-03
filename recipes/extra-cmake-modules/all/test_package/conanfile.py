from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import can_run
from conan.tools.microsoft import is_msvc
import os

class ExtraCMakeModulesTestConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"

    def build_requirements(self):
        self.test_requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            progname = "example"
            if is_msvc(self):
                progname += ".exe"

            self.output.info(f"buildpath: {self.folders.build}")
            self.output.info(f"buildpath2: {self.cpp.build.bindir}")
            runpath = os.path.join(self.folders.build, progname)
            self.run(runpath, env="conanrun")
