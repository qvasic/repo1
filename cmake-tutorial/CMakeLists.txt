cmake_minimum_required(VERSION 2.8.12)

project(cmake-tutorial)

set (cmake_tutorial_VERMAJ 1)
set (cmake_tutorial_VERMIN 666)
option( USE_METH "do meth, DO FUCKING METH!!" ON )

configure_file(
        "${PROJECT_SOURCE_DIR}/cmake-tutorial-config.h.in"
        "${PROJECT_BINARY_DIR}/cmake-tutorial-config.h"
    )

include_directories( "${PROJECT_BINARY_DIR}" )
set(CMAKE_INCLUDE_CURRENT_DIR ON)

message( "whole project CMakeLists.txt" )
message( "PROJECT_NAME=${PROJECT_NAME}" )
message( "PROJECT_SOURCE_DIR=${PROJECT_SOURCE_DIR}" )
message( "PROJECT_BINARY_DIR=${PROJECT_BINARY_DIR}" )
message( "CMAKE_SOURCE_DIR=${CMAKE_SOURCE_DIR}" )
message( "CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}" )
message( "CMAKE_CURRENT_SOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}" )
message( "CMAKE_CURRENT_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}" )
message( "CMAKE_COMMAND=${CMAKE_COMMAND}" )
message( "CMAKE_EXECUTABLE_SUFFIX=${CMAKE_EXECUTABLE_SUFFIX}")

if( USE_METH )
    add_subdirectory( my_meth_lab )
    include_directories( "${PROJECT_SOURCE_DIR}/my_meth_lab" )
endif()

add_executable(${PROJECT_NAME} "main.cpp")

if( USE_METH )
    target_link_libraries( ${PROJECT_NAME} my_meth_lab )
endif()

find_package( PythonInterp )

file( COPY runtest.py test-expect test-input DESTINATION . )

if( PYTHONINTERP_FOUND )
    message( "python ${PYTHON_VERSION_STRING} found, adding unit tests" )
    enable_testing()
    add_test( NAME test1 COMMAND ${PYTHON_EXECUTABLE} runtest.py
              ./${PROJECT_NAME} test-input test-expect )
else()
    message( "PYTHON INTERPRETER COULD NOT BE FOUND, TESTS CANNOT BE RUN" )
endif()
