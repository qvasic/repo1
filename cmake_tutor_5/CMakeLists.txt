cmake_minimum_required(VERSION 2.8.12)
project( cmake_tutor_5 )

find_package( PythonInterp )
if( PYTHONINTERP_FOUND )
    message( "python interp found, ver: ${PYTHON_VERSION_STRING}" )
    add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/sqrt_table.cpp
        COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/gen_sqrt_table.py 26 ${CMAKE_CURRENT_BINARY_DIR}/sqrt_table.cpp
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/gen_sqrt_table.py
    )
else()
    message( "couldn't find python interp, unable to continue" FATAL_ERROR )
endif()

add_executable( ${PROJECT_NAME} cmake_tutor_5.cpp ${CMAKE_CURRENT_BINARY_DIR}/sqrt_table.cpp )
