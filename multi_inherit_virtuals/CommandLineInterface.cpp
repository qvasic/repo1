#include "CommandLineInterface.h"

#include <iostream>

namespace vdem
{

CommandLineInterface::CommandLineInterface( const std::string& prompt, int status_length )
    : m_status_length( status_length )
    , m_blank_line( status_length, ' ' )
    , m_prompt( prompt )
{
}

CommandLineInterface::~CommandLineInterface( )
{
    std::cout << std::endl;
}

void CommandLineInterface::clear_status_line( )
{
    std::cout << '\r' << m_blank_line << '\r';
}

void
CommandLineInterface::update_status_on_screen( const std::string& status )
{
    clear_status_line( );
    std::cout << status.substr( 0, m_status_length ) << std::flush;
}

void
CommandLineInterface::set_status( const std::string& status )
{
    std::unique_lock< std::mutex > io_lock( m_io_mutex, std::try_to_lock );
    std::lock_guard< std::mutex > data_lock( m_data_mutex );

    if ( io_lock.owns_lock( ) )
    {
        clear_status_line( );
        print_unprinted_messages_and_clear( );
        update_status_on_screen( status );
    }

    m_last_status = status;
}

void
CommandLineInterface::print_unprinted_messages_and_clear( )
{
    if ( !m_unprinted_messages.empty( ) )
    {
        for ( const auto& unprinted_message : m_unprinted_messages )
        {
            std::cout << unprinted_message << std::endl;
        }
        m_unprinted_messages.clear( );
    }
}

void
CommandLineInterface::print_message( const std::string& message )
{
    std::unique_lock< std::mutex > io_lock( m_io_mutex, std::try_to_lock );
    std::lock_guard< std::mutex > data_lock( m_data_mutex );

    if ( io_lock.owns_lock( ) )
    {
        clear_status_line( );
        print_unprinted_messages_and_clear( );
        std::cout << message << std::endl;
        update_status_on_screen( m_last_status );
    }
    else
    {
        m_unprinted_messages.push_back( message );
    }
}

std::string
CommandLineInterface::wait_for_next_command( )
{
    std::string command;
    std::getline( std::cin, command );

    {
        std::lock_guard< std::mutex > io_lock( m_io_mutex );

        {
            std::lock_guard< std::mutex > data_lock( m_data_mutex );
            print_unprinted_messages_and_clear( );
        }

        std::cout << m_prompt;
        std::getline( std::cin, command );

        {
            std::lock_guard< std::mutex > data_lock( m_data_mutex );
            print_unprinted_messages_and_clear( );
            update_status_on_screen( m_last_status );
        }
    }

    return command;
}

bool
CommandLineInterface::is_eof( ) const
{
    return std::cin.eof( );
}

} // namespace vdem
