#include "ConsoleReader.h"

#include <iostream>
#include <algorithm>

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

bool
ConsoleReader::poll_input( )
{
    constexpr size_t input_buffer_size = 100;
    char input_buffer[ input_buffer_size ] = "";

    const size_t characters_read = std::cin.readsome( input_buffer, input_buffer_size-1 );
    input_buffer[ characters_read ] = '\0';
    m_unfinished_line += input_buffer;

    for ( ;; )
    {
        auto newline_position = std::find( std::begin( m_unfinished_line ),
                                           std::end( m_unfinished_line ),
                                           '\n' );

        if ( newline_position == std::end( m_unfinished_line ) )
        {
            break;
        }

        notify_listeners( std::string( std::begin( m_unfinished_line ), newline_position ) );
        m_unfinished_line = std::string( newline_position+1, std::end( m_unfinished_line ) );
    }

    return !std::cin.eof( );
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
