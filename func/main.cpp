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
    ASSERT_FALSE( default_constructed_func );
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

    ASSERT_TRUE( called );
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
    CallableSignal called;
    q::func< void, int > first_func( [ &called ]( int ){ called( ); } );
    q::func< void, int > second_func;

    ASSERT_TRUE( first_func );
    ASSERT_FALSE( called );
    ASSERT_DOES_NOT_THROW( first_func, 10 );
    ASSERT_TRUE( called );
    called.reset( );

    ASSERT_FALSE( second_func );
    ASSERT_THROWS< q::bad_func_call >( second_func, 10 );

    second_func = std::move( first_func );

    ASSERT_FALSE( first_func );
    ASSERT_THROWS< q::bad_func_call >( first_func, 10 );

    ASSERT_TRUE( second_func );
    ASSERT_FALSE( called );
    ASSERT_DOES_NOT_THROW( second_func, 10 );
    ASSERT_TRUE( called );
    called.reset( );
}

TEST( funcTests, CopyConstructible )
{
    CallableSignal called;
    q::func< void, int > first_func( [ &called ]( int ){ called( ); } );

    ASSERT_TRUE( first_func );
    ASSERT_FALSE( called );
    ASSERT_DOES_NOT_THROW( first_func, 10 );
    ASSERT_TRUE( called );
    called.reset( );

    q::func< void, int > second_func( first_func );

    ASSERT_TRUE( second_func );
    ASSERT_FALSE( called );
    ASSERT_DOES_NOT_THROW( second_func, 10 );
    ASSERT_TRUE( called );
    called.reset( );
}

TEST( funcTests, CopyConstructibleFromEmpty )
{
    q::func< void, int > first_func;

    ASSERT_FALSE( first_func );
    ASSERT_THROWS< q::bad_func_call >( first_func, 10 );

    q::func< void, int > second_func( first_func );

    ASSERT_FALSE( second_func );
    ASSERT_THROWS< q::bad_func_call >( second_func, 10 );
}

TEST( funcTests, CopyAssignable )
{
    CallableSignal called1, called2;

    q::func< void, int > first_func( [ &called1 ]( int ){ called1( ); } );

    ASSERT_TRUE( first_func );
    ASSERT_FALSE( called1 );
    ASSERT_DOES_NOT_THROW( first_func, 10 );
    ASSERT_TRUE( called1 );
    called1.reset( );

    q::func< void, int > second_func( [ &called2 ]( int ){ called2( ); } );

    ASSERT_TRUE( second_func );
    ASSERT_FALSE( called2 );
    ASSERT_DOES_NOT_THROW( second_func, 10 );
    ASSERT_TRUE( called2 );
    called2.reset( );

    second_func = first_func;

    ASSERT_TRUE( second_func );
    ASSERT_FALSE( called1 );
    ASSERT_FALSE( called2 );
    ASSERT_DOES_NOT_THROW( second_func, 10 );
    ASSERT_TRUE( called1 );
    ASSERT_FALSE( called2 );
    called1.reset( );
    called2.reset( );
}

TEST( funcTests, CopyAssignableFromItself )
{
    CallableSignal called;
    q::func< void, int > func( [ &called ]( int ){ called( ); } );

    ASSERT_TRUE( func );
    ASSERT_FALSE( called );
    ASSERT_DOES_NOT_THROW( func, 10 );
    ASSERT_TRUE( called );
    called.reset( );

    func = func;

    ASSERT_TRUE( func );
    ASSERT_FALSE( called );
    ASSERT_DOES_NOT_THROW( func, 10 );
    ASSERT_TRUE( called );
    called.reset( );
}

TEST( funcTests, CopyAssignableFromEmpty )
{
    CallableSignal called;
    q::func< void, int > first_func( [ &called ]( int ){ called( ); } );

    ASSERT_TRUE( first_func );
    ASSERT_FALSE( called );
    ASSERT_DOES_NOT_THROW( first_func, 10 );
    ASSERT_TRUE( called );
    called.reset( );

    q::func< void, int > second_func;

    ASSERT_FALSE( second_func );
    ASSERT_THROWS< q::bad_func_call >( second_func, 10 );

    first_func = second_func;

    /*ASSERT_FALSE( first_func );
    ASSERT_FALSE( called );
    ASSERT_THROWS< q::bad_func_call >( first_func, 10 );
    ASSERT_FALSE( called );*/
}





TEST( funcTests, Assignable )
{
    ASSERT_TRUE( false );
}

int main( int argc, char** argv )
{
    ::testing::InitGoogleTest( &argc, argv );
    return RUN_ALL_TESTS( );
}
