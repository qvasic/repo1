#include "CallableSignal.h"

CallableSignal::CallableSignal( )
    : m_set( false )
{
}

void
CallableSignal::set( )
{
    m_set = true;
}

void
CallableSignal::operator( )( )
{
    set( );
}

void
CallableSignal::reset( )
{
    m_set = false;
}

bool
CallableSignal::is_set( ) const
{
    return m_set;
}

CallableSignal::operator bool( ) const
{
    return is_set( );
}
