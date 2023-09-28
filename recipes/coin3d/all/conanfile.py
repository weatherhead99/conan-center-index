from conan import ConanFile
from conan.tools.files import get
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain

class Coin3DConan(ConanFile):
    name = "coin3D"
    settings = "os", "arch", "compiler", "build_type"

    options = {"shared" : [True, False],
               "threadsafe" : [True, False]}
    default_options = {"shared" : False,
                       "threadsafe" : False}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("expat/2.5.0")
        self.requires("zlib/1.2.13")
        self.requires("boost/1.83.0")
        self.requires("bzip2/1.0.8")
        self.requires("freetype/2.13.0")
        self.requires("opengl/system")
        self.requires("glu/system")
        self.requires("openal-soft/1.22.2")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_EXTERNAL_EXPAT"] = True
        tc.cache_variables["COIN_BUILD_TESTS"] = False

        tc.cache_variables["COIN_BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["COIN_THREADSAFE"] = self.options.threadsafe
        tc.cache_variables["ZLIB_RUNTIME_LINKING"] = False

        for lib in ["FREETYPE", "FONTCONFIG", "LIBBZIP2", "ZLIB", "GLU", "SIMAGE"]:
            tc.cache_variables[f"{lib}_RUNTIME_LINKING"] = False

        tc.cache_variables["COIN_VERBOSE"] = True

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()


    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()
