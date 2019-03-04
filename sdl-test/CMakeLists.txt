cmake_minimum_required( VERSION 3.5 )
project( sdl-test )
set( CMAKE_CXX_FLAGS "--std=c++11" )

set( SDL2_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}\\SDL2-2.0.9\\i686-w64-mingw32" )
include_directories( "${SDL2_DIRECTORY}\\include" )
link_directories( "${SDL2_DIRECTORY}\\lib" )
add_custom_target( SDL2DLL ALL
    ${CMAKE_COMMAND} -E copy "${SDL2_DIRECTORY}\\bin\\SDL2.dll" "${CMAKE_CURRENT_BINARY_DIR}"
    DEPENDS "${SDL2_DIRECTORY}\\bin\\SDL2.dll"
    BYPRODUCTS "${CMAKE_CURRENT_BINARY_DIR}\\SDL2.dll" )

add_executable( ${PROJECT_NAME} main.cpp )
target_link_libraries( ${PROJECT_NAME} mingw32 SDL2main SDL2 )
