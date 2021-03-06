#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class MbedTLS(ConanFile):
    name = "mbedtls"
    version = "2.6.1"
    description = "An open source, portable, easy to use, readable and flexible SSL library "
    url = "https://github.com/bincrafters/conan-mbedtls"
    license = "Apache-2.0"
    exports = ["LICENSE.md"]
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/library-CMakeLists.txt.patch"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False] }
    default_options = "shared=False"

    def source(self):
        source_url = "https://github.com/ARMmbed/mbedtls"
        archive_file = '{0}-{1}.tar.gz'.format(self.name, self.version)
        source_file = '{0}/archive/{1}'.format(source_url, archive_file)

        tools.download(source_file, archive_file)
        tools.untargz(archive_file)

        # in 2.6.1 there is a problem with the dir extracted,
        # it is mbedtls-mbedtls-2.6.1 instead of mbedtls-2.6.1
        os.rename('{0}-{0}-{1}'.format(self.name, self.version), 'sources')

        cmakelist_file = os.path.join("sources", "CMakeLists.txt")
        tools.replace_in_file(cmakelist_file, '${CMAKE_SOURCE_DIR}', '${CMAKE_SOURCE_DIR}/sources', strict=True)

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
        # the order below matters. If changed some linux builds may fail.
        self.cpp_info.libs = [ 'mbedx509', 'mbedcrypto', 'mbedtls' ]

        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.defines.append("MBEDTLS_PLATFORM_SNPRINTF_MACRO=snprintf")
