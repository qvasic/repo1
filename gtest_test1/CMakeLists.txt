project( gtest_test1 )

add_library( adder adder.h adder.cpp )
add_executable( adder_main main.cpp )
target_link_libraries( adder_main adder )

add_executable( adder_tests adder_tests.cpp )
target_link_libraries( adder_tests
    adder gtest pthread )
