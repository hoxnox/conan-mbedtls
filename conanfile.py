from conans import ConanFile, CMake, tools, os

class MbedTLS(ConanFile):
    name = "mbedTLS"
    version = "2.6.0"
    description = "An open source, portable, easy to use, readable and flexible SSL library "
    license = "https://github.com/ARMmbed/mbedtls/blob/development/apache-2.0.txt"
    url = "https://github.com/bincrafters/conan-mbedtls"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False] }
    default_options = "shared=False"
    lib_short_name = "mbedtls"
    generators = "cmake"
    
    def source(self):
        archive_name = self.lib_short_name + "-" + self.version
        extracted_folder = self.lib_short_name + "-" +archive_name
        source_url = "https://github.com/ARMmbed/mbedtls"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, archive_name))
        os.rename(extracted_folder, self.lib_short_name)
        
    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_TESTING"] = "Off"
        cmake.definitions["USE_SHARED_MBEDTLS_LIBRARY"] = "On"
        cmake.configure(source_dir=self.name)
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src=os.path.join(self.name, "include"))
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
            
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
