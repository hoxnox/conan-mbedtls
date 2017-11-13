from conans import ConanFile, tools, CMake, RunEnvironment
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        
    def test(self):
        bin_dir = os.path.join(os.getcwd(), "bin")
        lib_dir = os.path.join(os.getcwd(), "lib")
        with tools.environment_append(RunEnvironment(self).vars):
            if self.settings.os == "Windows":
                self.run(os.path.join("bin","test_package"))
            else:
                with tools.environment_append({"LD_LIBRARY_PATH": lib_dir, "DYLD_LIBRARY_PATH": lib_dir}):        
                    self.run(os.path.join("bin","test_package"))
