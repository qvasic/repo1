#include "ConsoleReader.h"

#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <atomic>
#include <mutex>
#include <vector>

class MyConsoleReaderListener : public ConsoleReaderListener
{
public:
    void
    on_new_line_read( const std::string& new_line ) override
    {
        std::cout << "NEW LINE RECIEVED: " << new_line << std::endl;
    }
};







#pragma once

#include <string>
#include <mutex>
#include <vector>

/*

  Simple command line interface.
  It is portable and thread-safe - relying only on C++11.

  It has a status line, every status line update will be printed on the same line, so it is
  suitable for showing progress status, distance to next maneuver, etc. Things that change often
  and you do not want to flood user with messages about every small change. Use set_status( ... )
  to update status line.

  If you really want to make user aware of something - use print_message( ... ). It will print
  a message on a separate line. It is suitable for more important events - calculation completion,
  passage of a turn, errors and warnings.

  Both set_status( ... ) and print_message( ... ) are thread-safe, you can call them
  from any thread.

  When you want to receive input from user - use wait_for_next_command( ). Unlike previous methods,
  this one is not thread-safe - call it only from one thread - UI thread. Once you called it,
  it will wait until user presses ENTER. Until then status line may be updated and messages printed.
  But once user pressed ENTER, status updates and new messages will not printed until whole input
  operation is done - there is no protable way to print something and allow user input at
  the same time.
  So, user presses ENTER, output is blocked, prompt is printed, and the sysem waits for user
  to enter a command and press ENTER one more time. Entered command is returned from
  wait_for_next_command( ), and unprinted messages and status updates are finally printed.

*/

namespace vdem
{

class CommandLineInterface
{
public:
    CommandLineInterface( const std::string& prompt = "> ", int status_length = 80 );

    CommandLineInterface( const CommandLineInterface& ) = delete;
    CommandLineInterface& operator=( const CommandLineInterface& ) = delete;

    CommandLineInterface( CommandLineInterface&& ) = default;
    CommandLineInterface& operator=( CommandLineInterface&& ) = default;

    ~CommandLineInterface( );

    void set_status( const std::string& status );
    void print_message( const std::string& message );
    std::string wait_for_next_command( );

private:
    void clear_status_line( );
    void update_status_on_screen( const std::string& status );
    void print_unprinted_messages_and_clear( );

private:
    int m_status_length;
    std::string m_blank_line;
    std::string m_prompt;

    std::mutex m_io_mutex;

    std::mutex m_data_mutex;
    std::string m_last_status;
    std::vector< std::string > m_unprinted_messages;
};

} // namespace vdem







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

} // namespace vdem






int main( )
{
vdem::CommandLineInterface command_line;

    std::atomic< bool > stop ( false );
    auto status_routine = [ &command_line, &stop ]( )
    {
        for ( size_t i = 0; !stop; ++i )
        {
            command_line.set_status( "status: " + std::to_string( i ) );
            std::this_thread::sleep_for( std::chrono::milliseconds( 1500 ) );
        }
    };
    std::thread status_thread( status_routine );

    auto message_routine = [ &command_line, &stop ]( )
    {
        for ( size_t i = 0; !stop; ++i )
        {
            command_line.print_message( "M message #" + std::to_string( i ) );
            std::this_thread::sleep_for( std::chrono::milliseconds( 7000 ) );
        }
    };
    std::thread message_thread( message_routine );

    while ( 1 )
    {
        std::string command = command_line.wait_for_next_command( );
        if ( command == "stop" )
        {
			command_line.print_message( "stopping and exiting..." );
            break;
        }
		else
		{
			command_line.print_message( "W unknown command" );
		}
    }

    stop = true;
    status_thread.join( );
    message_thread.join( );}
