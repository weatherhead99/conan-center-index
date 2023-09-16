from conan import ConanFile
from conan.tools.files import get
from conan.tools.cmake import cmake_layout

class VTKConan(ConanFile):
    name = "vtk"
    homepage = "https://vtk.org"
    description = "The Visualization Toolkit (VTK) is an open-source, freely available software system for 3D computer graphics, modeling, image processing, volume rendering, scientific visualization, and 2D plotting. "
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

