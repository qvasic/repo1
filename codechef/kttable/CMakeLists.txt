cmake_minimum_required(VERSION 2.8.12)
project( kttable )
set( CMAKE_CXX_FLAGS "--std=c++11" )
add_executable( ${PROJECT_NAME} kttable.cpp )

macro( print_one_two ONE TWO )
    message( "ONE: ${ONE}" )
    message( "TWO: ${TWO}" )
endmacro()

print_one_two( dwarfs bastards )
print_one_two( foxes rabbits )

message( "### looping" )
foreach( ITER IN LISTS "one two three" )
    message( "ITER: ${ITER}" )
endforeach( ITER )

find_package( PythonInterp 3 REQUIRED )
if( PYTHONINTERP_FOUND )
    message( "Python ${PYTHON_VERSION_STRING} found, adding unit testing" )

    # file ( COPY ... ) works only when cmake is re-run
    #file( COPY runtest.py test1-input test1-expected test2-input DESTINATION . )
    # configure_file ( ... COPYONLY ) works when make all is run
    #configure_file( test2-expected test2-expected COPYONLY )
    #add_test( NAME test1 COMMAND ${PYTHON_EXECUTABLE} runtest.py ./${PROJECT_NAME} test1-input test1-expected )
    #add_test( NAME test2 COMMAND ${PYTHON_EXECUTABLE} runtest.py ./${PROJECT_NAME} test2-input test2-expected )
    #add_dependencies( test1 ${PROJECT_NAME} )

    macro( add_test_expected_output TEST_NAME TEST_INPUT TEST_EXPECTED )
        add_test( NAME ${TEST_NAME}
                  COMMAND ${PYTHON_EXECUTABLE}
                          ${CMAKE_CURRENT_SOURCE_DIR}/runtest.py
                          ./${PROJECT_NAME}
                          ${CMAKE_CURRENT_SOURCE_DIR}/${TEST_INPUT}
                          ${CMAKE_CURRENT_SOURCE_DIR}/${TEST_EXPECTED}
        )
    endmacro( add_test_expected_output )
    add_test_expected_output( test1 test1-input test1-expected )
    add_test_expected_output( test2 test2-input test2-expected )

    enable_testing()
else()
    message( "COULDN'T FIND PYTHON INTERP, CANNOT PERFORM TESTING" FATAL_ERROR )
endif()
