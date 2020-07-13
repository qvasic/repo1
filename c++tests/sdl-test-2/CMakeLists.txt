cmake_minimum_required( VERSION 3.0 )
project( sdl-test )
set( CMAKE_CXX_FLAGS "--std=c++17" )

if ( WIN32 )
	# Windows
	set( SDL2_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}\\SDL2/SDL2-2.0.12\\x86_64-w64-mingw32" )
	include_directories( "${SDL2_DIRECTORY}\\include" )
	link_directories( "${SDL2_DIRECTORY}\\lib" )
	add_custom_target( SDL2DLL ALL
	    ${CMAKE_COMMAND} -E copy "${SDL2_DIRECTORY}\\bin\\SDL2.dll" "${CMAKE_CURRENT_BINARY_DIR}"
	    DEPENDS "${SDL2_DIRECTORY}\\bin\\SDL2.dll"
	    BYPRODUCTS "${CMAKE_CURRENT_BINARY_DIR}\\SDL2.dll" )
    set( SDL2_LIBRARIES mingw32 SDL2main SDL2 )
else( )
	# Not widnows, most likely Linux/Posix
	find_package( SDL2 REQUIRED )
	include_directories( ${SDL2_INCLUDE_DIRECTORIES} )
endif( )

add_executable( ${PROJECT_NAME} main.cpp SDLLibrary.h SDLLibrary.cpp GraphicalElement.h )
target_link_libraries( ${PROJECT_NAME} ${SDL2_LIBRARIES} )
