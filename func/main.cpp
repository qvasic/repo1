#include <iostream>
#include <gtest/gtest.h>
#include "func.h"
#include "CallableSignal.h"

template <typename E, typename T, typename ... A>
void ASSERT_THROWS( T& f, A ... arg )
{
    try
    {
        f( std::forward<A>( arg ) ... );
        ASSERT_TRUE( false );
    }
    catch( const E& )
    {
        ASSERT_TRUE( true );
    }
    catch( ... )
    {
        ASSERT_TRUE( false );
    }
}

template <typename T, typename ... A>
void ASSERT_DOES_NOT_THROW( T& f, A ... arg )
{
    try
    {
        f( std::forward<A>( arg ) ... );
        ASSERT_TRUE( true );
    }
    catch( ... )
    {
        ASSERT_TRUE( false );
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////

TEST( funcTests, DefaultConstructible )
{
    q::func< int, int > default_constructed_func;
    EXPECT_FALSE( default_constructed_func );
}

TEST( funcTests, EmptyThrows )
{
    q::func< int, int > default_constructed_func;
    ASSERT_THROWS< q::bad_func_call >( default_constructed_func, 10 );
}

TEST( funcTests, AssignedDoesNotThrow )
{
    q::func< int, int > assigned_func( []( int ){ return 0; } );
    ASSERT_TRUE( assigned_func );
    ASSERT_DOES_NOT_THROW( assigned_func, 10 );
}

TEST( funcTests, CallsPassedObject )
{
    CallableSignal called;
    q::func< void, int > func_to_verify( [ &called ]( int ){ called( ); } );
    func_to_verify( 10 );

    EXPECT_TRUE( called );
}

TEST( funcTests, MoveConstructible )
{
    CallableSignal called;
    q::func< void, int > first_func( [ &called ]( int ){ called( ); } );

    ASSERT_TRUE( first_func );
    ASSERT_DOES_NOT_THROW( first_func, 10 );

    called.reset( );
    first_func( 10 );
    ASSERT_TRUE( called );

    q::func< void, int > second_func( std::move( first_func ) );

    ASSERT_FALSE( first_func );
    ASSERT_THROWS< q::bad_func_call >( first_func, 10 );
    ASSERT_TRUE( second_func );
    ASSERT_DOES_NOT_THROW( second_func, 10 );

    called.reset( );
    second_func( 10 );
    ASSERT_TRUE( called );
}




TEST( funcTests, MoveAssignable )
{
    EXPECT_TRUE( false );
}
TEST( funcTests, CopyConstructible )
{
    EXPECT_TRUE( false );
}
TEST( funcTests, CopyAssignable )
{
    EXPECT_TRUE( false );
}
TEST( funcTests, Assignable )
{
    EXPECT_TRUE( false );
}





int main( int argc, char** argv )
{
    ::testing::InitGoogleTest( &argc, argv );
    return RUN_ALL_TESTS( );
}
