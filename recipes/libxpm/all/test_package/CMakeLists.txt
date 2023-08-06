cmake_minimum_required(VERSION 3.16)
project(test_package C)


#first, find deps using conan mechanisms (i.e. generated CMake package)
find_package(libxpm REQUIRED CONFIG)
add_executable(test_package_cmake test_package.c)
target_link_libraries(test_package_cmake PRIVATE libxpm::libxpm)


#now, find deps using pkgconfig (i.e. as might be done by a "regular"
#downstream autotools consumer

include(FindPkgConfig)
pkg_check_modules(PC_XPM REQUIRED "xpm")

if(NOT ${XPM_CONAN_VERSION} VERSION_EQUAL ${PC_XPM_VERSION})
  message(ERROR "conan version of xpm is supposed to be: ${XPM_CONAN_VERSION}")
  message(ERROR "but found version was: ${PC_XPM_VERSION}")
  message(ERROR "likely a system version of XPM was found instead")
  message(FATAL_ERROR "cannot continue testing package")
endif()

add_executable(test_package_pc test_package.c)
target_link_libraries(test_package_pc PRIVATE ${PC_XPM_LIBRARIES})
  


  
  
