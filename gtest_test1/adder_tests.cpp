#include <gtest/gtest.h>
#include "adder.h"

TEST( tests, test1 )
{
    EXPECT_EQ( 2, adder( 1, 1 ) );
}

int main( int argc, char *argv[] )
{
    ::testing::InitGoogleTest( &argc, argv );
    return RUN_ALL_TESTS();
}
