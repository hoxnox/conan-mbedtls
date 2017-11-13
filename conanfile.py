#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, os

class MbedTLS(ConanFile):
    name = "mbedtls"
    version = "2.6.1"
    description = "An open source, portable, easy to use, readable and flexible SSL library "
    license = "https://github.com/ARMmbed/mbedtls/blob/development/apache-2.0.txt"
    url = "https://github.com/bincrafters/conan-mbedtls"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False] }
    default_options = "shared=False"
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/library-CMakeLists.txt.patch"
    source_url = "https://github.com/ARMmbed/mbedtls"

    def source(self):
        archive_file = '{0}-{1}.tar.gz'.format(self.name, self.version)
        source_file = '{0}/archive/{1}'.format(self.source_url, archive_file)

        tools.download(source_file, archive_file)
        tools.untargz(archive_file)

        # in 2.6.1 there is a problem with the dir extracted,
        # it is mbedtls-mbedtls-2.6.1 instead of mbedtls-2.6.1
        os.rename('{0}-{0}-{1}'.format(self.name, self.version), 'sources')

    def build(self):

        if self.settings.os == "Windows":
            old_lib_cmake = os.path.join("sources", "library", "CMakeLists.txt")
            new_lib_cmake = os.path.join("patches", "library-CMakeLists.txt.patch")
            os.unlink(old_lib_cmake)
            os.rename(new_lib_cmake, old_lib_cmake)


        cmake = CMake(self)
        cmake.verbose = True
        cmake.definitions["ENABLE_TESTING"] = "Off"
        cmake.definitions["ENABLE_PROGRAMS"] = "Off"

        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = "On"

        if self.settings.compiler == 'Visual Studio':
            cmake.definitions["CMAKE_C_FLAGS"] = "-DMBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf"
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-DMBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf"

        if self.settings.compiler == 'gcc':
            if self.settings.arch == 'x86':
                cmake.definitions["CMAKE_C_FLAGS"] = "-m32"
                cmake.definitions["CMAKE_CXX_FLAGS"] = "-m32"
            else:
                cmake.definitions["CMAKE_C_FLAGS"] = "-m64"
                cmake.definitions["CMAKE_CXX_FLAGS"] = "-m64"
        
        cmake.definitions["USE_SHARED_MBEDTLS_LIBRARY"] = self.options.shared
        cmake.definitions["USE_STATIC_MBEDTLS_LIBRARY"] = not self.options.shared

        cmake.configure(source_dir="..", build_dir="build")
        cmake.build()
        cmake.install()
        
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
            self.cpp_info.defines.append("MBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf")
