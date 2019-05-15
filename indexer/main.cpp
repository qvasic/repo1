#include <sqlite3.h>
#include <boost/filesystem.hpp>
#include <boost/format.hpp>

#include <fstream>
#include <iostream>
#include <vector>
#include <map>

#include <cctype>

std::vector< std::pair< std::string, size_t > >
break_line( const std::string& line )
{
    std::vector< std::pair< std::string, size_t > > words;

    auto word_end = std::begin( line );

    for (;;)
    {
        auto word_start = std::find_if( word_end, std::end( line ),
                                        []( char ch ){ return std::isalpha( ch ); } );

        if ( word_start == std::end( line ) )
        {
            break;
        }

        word_end = std::find_if( word_start, std::end( line ),
                                 []( char ch ){ return !std::isalpha( ch ); } );

        std::string current_word;

        std::copy( word_start, word_end, std::back_inserter( current_word ) );

        words.push_back( std::make_pair( current_word, word_start - std::begin( line ) ) );
    }

    return words;
}

template <typename F, typename S>
std::ostream& operator<<( std::ostream& os, const std::pair< F, S >& pair )
{
    os << "first=" << pair.first << " second=" << pair.second;
    return os;
}

template <typename T>
std::ostream& operator<<( std::ostream& os, const std::vector< T >& vec )
{
    for ( auto i = std::begin( vec ); i != std::end( vec ); ++i )
    {
        os << *i << ' ';
    }

    return os;
}

std::ostream& operator<<( std::ostream& os,
                const std::map< std::string, std::vector< std::pair< size_t, size_t > > >& words )
{
    for ( const auto& word : words )
    {
        os << word.first << ' ';

        for ( const auto& occurrence : word.second )
        {
            os << boost::format( "line=%|| char=%|| " ) % occurrence.first % occurrence.second;
        }

        os << std::endl;
    }

    return os;
}

std::string
tolower( const std::string& original )
{
    std::string converted( original.size( ), ' ' );

    for ( size_t i = 0; i < original.size( ); ++i )
    {
        converted[ i ] = std::tolower( original[ i ] );
    }

    return converted;
}

int main( )
{
    //auto& input_file = std::cin;
    std::ifstream input_file( "test.txt" );

    std::map< std::string, std::vector< std::pair< size_t, size_t > > > words;
    int line_number = 0;

    while ( input_file )
    {
        std::string line;
        std::getline( input_file, line );

        for ( const auto& word : break_line( line ) )
        {
            words[ tolower( word.first ) ].push_back( std::make_pair( line_number, word.second ) );
        }

        //std::cout << break_line( line ) << std::endl;
        ++line_number;
    }

    std::cout << words;

    /*
    sqlite3* handle = nullptr;

    if( sqlite3_open( "index.db", &handle ) == SQLITE_OK )
    {
        std::cout << "database was opened" << std::endl;
    }

    if ( handle )
    {
        sqlite3_close( handle );
    }
    */
}
