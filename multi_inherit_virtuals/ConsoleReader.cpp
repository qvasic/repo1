#include "ConsoleReader.h"

#include <iostream>
#include <algorithm>

ConsoleReader::ConsoleReader( vdem::CommandLineInterface& cli )
    : m_cli( cli )
{
}

void
ConsoleReader::add_listener( ConsoleReaderListener* listener )
{
    m_listeners.insert( listener );
}

void
ConsoleReader::remove_listener( ConsoleReaderListener* listener )
{
    m_listeners.erase( listener );
}

void
ConsoleReader::run( )
{
    m_cli.print_message( "enter stop to stop" );

    for ( ; ; )
    {
        std::string command = m_cli.wait_for_next_command( );

        if ( command == "stop" || m_cli.is_eof( ) )
        {
            break;
        }

        notify_listeners( command );
    }
}

void
ConsoleReader::notify_listeners( const std::string& new_line )
{
    auto call_listener = [ &new_line ]( ConsoleReaderListener* listener_ptr )
    {
        listener_ptr->on_new_line_read( new_line );
    };

    std::for_each( std::begin( m_listeners ), std::end( m_listeners ), call_listener );
}
