#include "ConsoleReader.h"

#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <atomic>
#include <mutex>

class MyConsoleReaderListener : public ConsoleReaderListener
{
public:
    void
    on_new_line_read( const std::string& new_line ) override
    {
        std::cout << "NEW LINE RECIEVED: " << new_line << std::endl;
    }
};

namespace
{

class CommandLineWithStatus
{
public:
    CommandLineWithStatus( const std::string& prompt = "> ", int status_length = 80 );
    void set_status( const std::string& status );
    std::string wait_for_next_command( );

private:
    int m_status_length;
    std::string m_blank_line;
    std::string m_prompt;
    std::mutex m_prompt_mutex;
};

CommandLineWithStatus::CommandLineWithStatus( const std::string& prompt, int status_length )
    : m_status_length( status_length )
    , m_blank_line( status_length, ' ' )
    , m_prompt( prompt )
{}

void
CommandLineWithStatus::set_status( const std::string& status )
{
    if ( m_prompt_mutex.try_lock( ) )
    {
        std::cout << '\r' << m_blank_line << '\r';
        std::cout << status.substr( 0, m_status_length );
        // exception safety?!
        m_prompt_mutex.unlock( );
    }
}

std::string
CommandLineWithStatus::wait_for_next_command( )
{
    std::string command;
    std::getline( std::cin, command );

    std::lock_guard< std::mutex > lock( m_prompt_mutex );
    std::cout << m_prompt;
    std::getline( std::cin, command );
    return command;
}

}

int main( )
{
    for ( int i=0; i<200; ++i )
    {
        std::cout << '\r' << i;
        std::this_thread::sleep_for( std::chrono::milliseconds( 10
                                                                0 ) );
    }

    CommandLineWithStatus command_line;

    std::atomic< bool > stop ( false );
    auto counter_routine = [ &command_line, &stop ]( )
    {
        for ( size_t i = 0; !stop; ++i )
        {
            command_line.set_status( std::to_string( i ) );
            std::this_thread::sleep_for( std::chrono::milliseconds( 250 ) );
        }
    };
    std::thread counter_thread( counter_routine );

    while ( 1 )
    {
        std::string command = command_line.wait_for_next_command( );
        if ( command == "stop" )
        {
            break;
        }
    }

    stop = true;
    counter_thread.join( );
}
