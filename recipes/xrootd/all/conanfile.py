from conan import ConanFile
from conan.tools.files import get
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain

class XRootDConan(ConanFile):
    name = "xrootd"
    settings = "os", "compiler", "arch", "build_type"

    requires = ("tinyxml/2.6.2", "libuuid/1.0.3", "zlib/1.2.13",
                "libxml2/2.11.4", "json-c/0.17", "libfuse/3.10.5",
                "readline/8.1.2", "openssl/1.1.1v")


    options = {"with_fuse" : [True, False]}

    default_options = {"with_fuse" : True}

    def config_options(self):
        if self.settings.os != "Linux":
            #note XRootD doesn't support macfuse
            del self.options.with_fuse

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination = self.source_folder, strip_root=True)

        
    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["FORCE_ENABLED"] = True

        tc.cache_variables["ENABLE_KRB5"] = False
        tc.cache_variables["ENABLE_MACAROONS"] = False
        tc.cache_variables["ENABLE_SCITOKENS"] = False
        tc.cache_variables["ENABLE_VOMS"] = False
        tc.cache_variables["ENABLE_XRDCLHTTP"] = False

        if self.options.with_fuse:
            tc.cache_variables["ENABLE_FUSE"] = True

        tc.generate()

        deps = CMakeDeps(self)

        deps.set_property("libuuid", "cmake_target_name", "uuid::uuid")
        deps.set_property("readline", "cmake_file_name" ,"Readline")
        deps.set_property("libfuse", "cmake_file_name", "fuse")
        deps.generate()


    def build(self):
        cm = CMake(self)
#        cm.configure(cli_args=["--debug-find"])
        cm.configure()
        cm.build()
