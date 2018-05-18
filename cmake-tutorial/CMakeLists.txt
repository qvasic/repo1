cmake_minimum_required(VERSION 2.8.12)

project(cmake-tutorial)

set (cmake_tutorial_VERMAJ 1)
set (cmake_tutorial_VERMIN 666)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

message( "PROJECT_NAME=${PROJECT_NAME}" )
message( "PROJECT_SOURCE_DIR=${PROJECT_SOURCE_DIR}" )
message( "PROJECT_BINARY_DIR=${PROJECT_BINARY_DIR}" )
message( "CMAKE_SOURCE_DIR=${CMAKE_SOURCE_DIR}" )
message( "CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}" )
message( "CMAKE_COMMAND=${CMAKE_COMMAND}" )

configure_file(
        "${PROJECT_SOURCE_DIR}/cmake-tutorial-config.h.in"
        "${PROJECT_BINARY_DIR}/cmake-tutorial-config.h"
    )

include_directories( "${PROJECT_BINARY_DIR}" )

add_subdirectory( my_meth_lab )
include_directories( "${PROJECT_SOURCE_DIR}/my_meth_lab" )

add_executable(${PROJECT_NAME} "main.cpp")
target_link_libraries( ${PROJECT_NAME} my_meth_lab )

find_package( PythonInterp )

if( PYTHONINTERP_FOUND )
    message( "python ${PYTHON_VERSION_STRING} found, adding unit tests" )
    enable_testing()
    add_test( NAME test1 COMMAND ${PYTHON_EXECUTABLE} ${PROJECT_SOURCE_DIR}/runtest.py
              ./${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/test-input ${PROJECT_SOURCE_DIR}/test-expect )
else()
    message( "PYTHON INTERPRETER COULD NOT BE FOUND, TESTS CANNOT BE RUN" )
endif()
