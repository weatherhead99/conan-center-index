from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout


class gengenTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.test_requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def test(self):
        if can_run(self):
            self.run("gengen --version", env="conanrun")
