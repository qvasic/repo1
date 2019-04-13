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
#include <cassert>

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

class alternative_console_reader
{
public:
    alternative_console_reader( vdem::CommandLineInterface& cli,
                                const std::string& tag )
        : m_listener_data{ dispatcher_routine }
        , m_tag( tag )
        , m_cli( cli )
    {
        assert( this == static_cast< void* >( &m_listener_data ) );
    }
    operator ConsoleReaderAlternativeListener*( )
    {
        return &m_listener_data;
    }

private:
     static void dispatcher_routine( ConsoleReaderAlternativeListener* listener_obj,
                                     const std::string& new_line )
     {
         static_cast< alternative_console_reader* >( static_cast< void* >( listener_obj ) )
                 ->on_new_line_read( new_line );
     }
     void on_new_line_read( const std::string& new_line )
     {
         m_cli.print_message( m_tag + new_line );
     }

private:
    ConsoleReaderAlternativeListener m_listener_data;
    std::string m_tag;
    vdem::CommandLineInterface& m_cli;
};

class alternative_console_reader_with_storage
{
public:
    alternative_console_reader_with_storage( vdem::CommandLineInterface& cli )
        : m_cli( cli )
        , m_listener_obj{ listener_dispatcher }
    {
    }
    operator ConsoleReaderAlternativeListener*( )
    {
        return &m_listener_obj;
    }

private:
    static void listener_dispatcher( ConsoleReaderAlternativeListener* listener_obj_ptr,
                                     const std::string& line )
    {
        constexpr auto listener_obj_offset_ptr
                = &static_cast< alternative_console_reader_with_storage* >( nullptr )->m_listener_obj;
        constexpr auto listener_obj_offset
                = reinterpret_cast< char* >( listener_obj_offset_ptr ) - static_cast< char* >( nullptr );
        alternative_console_reader_with_storage* derived_obj_ptr
                = reinterpret_cast< alternative_console_reader_with_storage* >(
                    reinterpret_cast< char* >( listener_obj_ptr ) - listener_obj_offset );

        derived_obj_ptr->on_new_line_read( line );
    }
    void on_new_line_read( const std::string& line )
    {
        std::string message = "THIS IS NEW SHIT: \"" + line + "\" ALL THE OLD SHIT:";
        std::for_each( std::begin( m_previous_lines ), std::end( m_previous_lines ),
                       [ &message ]( const std::string& old_line )
                       {
                            message += " \"" + old_line + "\"";
                       } );
        m_cli.print_message( message );

        m_previous_lines.push_back( line );
    }

private:
    std::vector< std::string > m_previous_lines;
    ConsoleReaderAlternativeListener m_listener_obj;
    vdem::CommandLineInterface& m_cli;
};

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

    ConsoleReader console_reader( command_line );

    MyConsoleReaderListener listener1( command_line );
    ConsoleReaderListenerWithStorage listener2( command_line );
    alternative_console_reader listener3( command_line, "NEW NEW NEW: " );
    alternative_console_reader_with_storage listener4( command_line );

    console_reader.add_listener( &listener1 );
    console_reader.add_listener( &listener2 );
    console_reader.add_listener( listener3 );
    console_reader.add_listener( listener4 );

    console_reader.run( );

    command_line.print_message( "stopping..." );
    stop = true;
    status_thread.join( );
    message_thread.join( );}
