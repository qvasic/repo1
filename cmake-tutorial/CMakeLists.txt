cmake_minimum_required(VERSION 2.8.12)

project(cmake-tutorial)

set (cmake_tutorial_VERMAJ 1)
set (cmake_tutorial_VERMIN 666)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)

configure_file(
        "${PROJECT_SOURCE_DIR}/cmake-tutorial-config.h.in"
        "${PROJECT_BINARY_DIR}/cmake-tutorial-config.h"
    )

include_directories( "${PROJECT_BINARY_DIR}" )

add_subdirectory( my_meth_lab )
include_directories( "${PROJECT_SOURCE_DIR}/my_meth_lab" )

add_executable(${PROJECT_NAME} "main.cpp")
target_link_libraries( ${PROJECT_NAME} my_meth_lab )
