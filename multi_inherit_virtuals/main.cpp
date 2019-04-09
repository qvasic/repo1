#include "ConsoleReader.h"
#include "CommandLineInterface.h"

#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <atomic>
#include <mutex>
#include <vector>
#include <algorithm>

class MyConsoleReaderListener : public ConsoleReaderListener
{
public:
    MyConsoleReaderListener( vdem::CommandLineInterface& cli )
        : m_cli( cli )
    {
    }

    void
    on_new_line_read( const std::string& new_line ) override
    {
        m_cli.print_message( "NEW LINE RECIEVED: " + new_line );
    }

private:
    vdem::CommandLineInterface& m_cli;
};

 class ConsoleReaderListenerWithStorage : public std::vector< std::string >
                                        , public ConsoleReaderListener
 {
 public:
     ConsoleReaderListenerWithStorage( vdem::CommandLineInterface& cli )
         : m_cli( cli )
     {
     }

     void
     on_new_line_read( const std::string& new_line ) override
     {
         this->push_back( new_line );
         std::string message = "NEW LINE RECIEVED, SO FAR WE'VE GOT THIS:";
         std::for_each( std::begin( *this ), std::end( *this ),
                        [ &message ]( const std::string& str )
                        {
                            message += " \"" + str + "\"";
                        }
            );

         m_cli.print_message( message );
     }

 private:
    vdem::CommandLineInterface& m_cli;
 };

int main( )
{
    vdem::CommandLineInterface command_line;
    ConsoleReader console_reader( command_line );
    MyConsoleReaderListener listener1( command_line );
    ConsoleReaderListenerWithStorage listener2( command_line );
    console_reader.add_listener( &listener1 );
    console_reader.add_listener( &listener2 );

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

    console_reader.run( );

    command_line.print_message( "stopping..." );
    stop = true;
    status_thread.join( );
    message_thread.join( );}
