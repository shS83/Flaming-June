cmake_minimum_required(VERSION 3.16)
project(FlamingJune LANGUAGES CXX)

find_package(PkgConfig REQUIRED)
pkg_check_modules(SDL2 REQUIRED IMPORTED_TARGET sdl2)
pkg_check_modules(SDL2_TTF REQUIRED IMPORTED_TARGET SDL2_ttf)

add_executable(flaming-june flaming_june-mod.cpp)
target_compile_features(flaming-june PRIVATE cxx_std_17)
target_compile_options(flaming-june PRIVATE -Wall -Wextra -Wpedantic)
target_link_libraries(flaming-june PRIVATE PkgConfig::SDL2 PkgConfig::SDL2_TTF)
configure_file(VINERITC.TTF VINERITC.TTF COPYONLY)
