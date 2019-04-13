cmake_minimum_required( VERSION 3.5 )
project( multi_inherit_virtuals )
set( CMAKE_CXX_STANDARD "11" )
if( UNIX )
    set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread" )
endif( UNIX )

add_executable( multi_inherit_virtuals main.cpp
                ConsoleReader.cpp ConsoleReader.h
                CommandLineInterface.h CommandLineInterface.cpp
              )

