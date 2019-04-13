#pragma once

#include "CommandLineInterface.h"

#include <string>
#include <set>

class ConsoleReaderListener
{
public:
    virtual void on_new_line_read( const std::string& line ){ }
    virtual ~ConsoleReaderListener( ) = default;
};

struct ConsoleReaderAlternativeListener;
using CallbackWithStrParam = void (*)( ConsoleReaderAlternativeListener*, const std::string& );
struct ConsoleReaderAlternativeListener
{
    CallbackWithStrParam on_new_line_read;
};

class ConsoleReader
{
public:
    ConsoleReader( vdem::CommandLineInterface& cli );

    void run( );

    void add_listener( ConsoleReaderListener* listener );
    void remove_listener( ConsoleReaderListener* listener );

    void add_listener( ConsoleReaderAlternativeListener* listener );
    void remove_listener( ConsoleReaderAlternativeListener* listener );

private:
    void notify_listeners( const std::string& new_line );

private:
    vdem::CommandLineInterface& m_cli;
    std::string m_unfinished_line;
    std::set< ConsoleReaderListener* > m_listeners; // not owned
    std::set< ConsoleReaderAlternativeListener* > m_alternative_listeners; // not owned
};
