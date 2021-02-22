#pragma once

#include <iostream>
#include <thread>
#include <mutex>

namespace q
{

namespace
{

std::string
multiply_string( const std::string& str, size_t times )
{
    std::string result;

    for ( size_t i = 0; i < times; ++i )
    {
        result += str;
    }

    return result;
}

} // anonymous

class logger
{
public:
    enum class INDENT
    {
        NONE,
        INDENT,
        UNINDENT
    };

public:
    template < typename T >
    void print( T&& t, INDENT indent = INDENT::NONE )
    {
        return;
        std::lock_guard< std::mutex > guard( m_mutex );
        auto& thread_info = get_thread_info( );

        if ( indent == INDENT::UNINDENT )
        {
            --thread_info.second;
        }

        std::cout << "thread #" << thread_info.first << " "
                  << multiply_string( "\t", thread_info.second ) << std::forward< T >( t )
                  << std::endl;

        if ( indent == INDENT::INDENT )
        {
            ++thread_info.second;
        }
    }

    static logger&
    get_logger( )
    {
        static logger Logger;
        return Logger;
    }

public:
    class scoped
    {
    public:
        explicit scoped( const std::string& tag )
            : m_tag( tag )
        {
            logger::get_logger( ).print( m_tag + " {", INDENT::INDENT );
        }

        ~scoped( )
        {
            logger::get_logger( ).print( "} // " + m_tag, INDENT::UNINDENT );
        }

    private:
        std::string m_tag;
    };

private:
    using thread_number_t = unsigned;
    using thread_info_t = std::pair< thread_number_t, unsigned >;

    logger( ) = default;

    thread_info_t&
    get_thread_info( )
    {
        const auto id = std::this_thread::get_id( );
        const auto search_iter = m_thread_numbers.find( id );
        if ( search_iter != m_thread_numbers.end( ) )
        {
            return search_iter->second;
        }

        const auto new_thread_info = thread_info_t( m_next_thread_number, 0 );
        ++m_next_thread_number;
        return m_thread_numbers[ id ] = new_thread_info;
    }

private:
    std::mutex m_mutex;
    std::map< std::thread::id, thread_info_t > m_thread_numbers;
    thread_number_t m_next_thread_number = 0;
};

}

