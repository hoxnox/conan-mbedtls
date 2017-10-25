from conans import ConanFile, CMake, tools, os

class MbedTLS(ConanFile):
    name = "mbedtls"
    version = "2.6.0"
    description = "An open source, portable, easy to use, readable and flexible SSL library "
    license = "https://github.com/ARMmbed/mbedtls/blob/development/apache-2.0.txt"
    url = "https://github.com/bincrafters/conan-mbedtls"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False] }
    default_options = "shared=False"
    generators = "cmake"
    
    def source(self):
        archive_name = self.name + "-" + self.version
        extracted_folder = self.name + "-" +archive_name
        source_url = "https://github.com/ARMmbed/mbedtls"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, archive_name))
        os.rename(extracted_folder, self.name)
        
    def build(self):
        self.cmake = CMake(self)
        #self.cmake.verbose = True
        self.cmake.definitions["ENABLE_TESTING"] = "Off"

        if self.settings.os == "Windows":
            self.cpp_info.defines.append("MBEDTLS_PLATFORM_C")
			
        if self.settings.compiler == 'gcc':
            if self.settings.arch == 'x86':
                self.cmake.definitions["CMAKE_C_FLAGS"] = "-m32"
                self.cmake.definitions["CMAKE_CXX_FLAGS"] = "-m32"
            else:
                self.cmake.definitions["CMAKE_C_FLAGS"] = "-m64"
                self.cmake.definitions["CMAKE_CXX_FLAGS"] = "-m64"
        
        self.cmake.definitions["USE_SHARED_MBEDTLS_LIBRARY"] = self.options.shared
        self.cmake.definitions["USE_STATIC_MBEDTLS_LIBRARY"] = not self.options.shared

        self.cmake.configure(source_dir=self.name)
        self.cmake.build()
        
    def package(self):   
        self.copy("*.h", dst="include", src=os.path.join(self.name, 'include'), keep_path=True)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False, symlinks=True)
                
        if self.options.shared:
            self.copy("*.so*", dst="lib", keep_path=False, symlinks=True)
        else:
            self.copy("*.a", dst="lib", keep_path=False, symlinks=True)
            
        self.copy("*.lib", dst="lib", keep_path=False, symlinks=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
		
        if self.settings.os == "Windows":
            self.cpp_info.defines.append("MBEDTLS_PLATFORM_C")