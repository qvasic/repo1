#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>

#include "nmea.h"

int main( )
{
    int failed = 0;

    struct checksum_cases_type
    {
        std::string argument;
        std::string expected;
    };

    std::vector< checksum_cases_type > checksum_cases = {
        { "",       "00" },
        { "1",      "31" },
        { "11",     "00" },
        { "1 1",    "20" },
        { "12",     "03" },
        { "GPGLL,0000.0000,N,00000.0000,E", "6B" },
    };

    for( const auto& testcase : checksum_cases )
    {
        auto actual = nmea::checksum( testcase.argument );
        if( actual != testcase.expected )
        {
            std::cout << "FAILED nmea::checksum( " << testcase.argument
                      << " ) returned " << actual
                      << " while " << testcase.expected << " was expected" << std::endl;
            ++failed;
        }
        else
        {
            std::cout << "passed" << std::endl;
        }
    }

    std::cout << "utc_time_str: " << nmea::utc_time_str( ) << std::endl;
    std::cout << "utc_time_str: " << nmea::utc_time_str( ) << std::endl;
    std::this_thread::sleep_for( std::chrono::milliseconds( 20 ) );
    std::cout << "utc_time_str: " << nmea::utc_time_str( ) << std::endl;
    std::cout << "utc_time_str: " << nmea::utc_time_str( ) << std::endl;
    std::this_thread::sleep_for( std::chrono::milliseconds( 97 ) );
    std::cout << "utc_time_str: " << nmea::utc_time_str( ) << std::endl;
    std::cout << "utc_time_str: " << nmea::utc_time_str( ) << std::endl;

    std::cout << "utc_date_str: " << nmea::utc_date_str( ) << std::endl;

    struct coords_cases_type
    {
        double arg_coord;
        std::string expected;
    };

    std::vector< coords_cases_type > lat_cases = {
        { 0, "0000.0000,N" },
        { 1, "0100.0000,N" },
        { -1, "0100.0000,S" },
        { 30, "3000.0000,N" },
        { 30.211, "3012.6600,N" },
        { -30.211, "3012.6600,S" },
    };

    for( const auto& testcase : lat_cases )
    {
        auto actual = nmea::lat_to_nmea_str( testcase.arg_coord );
        if( actual != testcase.expected )
        {
            std::cout << "FAILED nmea::lat_to_nmea_str( " << testcase.arg_coord
                      << " ) returned " << actual
                      << " while " << testcase.expected << " was expected" << std::endl;
            ++failed;
        }
        else
        {
            std::cout << "passed" << std::endl;
        }
    }

    std::vector< coords_cases_type > lng_cases = {
        { 0, "00000.0000,E" },
        { 1, "00100.0000,E" },
        { -1, "00100.0000,W" },
        { 30, "03000.0000,E" },
        { 30.211, "03012.6600,E" },
        { -30.211, "03012.6600,W" },
        { -89, "08900.0000,W" },
        { 179.90, "17954.0000,E" },

    };

    for( const auto& testcase : lng_cases )
    {
        auto actual = nmea::lng_to_nmea_str( testcase.arg_coord );
        if( actual != testcase.expected )
        {
            std::cout << "FAILED nmea::lng_to_nmea_str( " << testcase.arg_coord
                      << " ) returned " << actual
                      << " while " << testcase.expected << " was expected" << std::endl;
            ++failed;
        }
        else
        {
            std::cout << "passed" << std::endl;
        }
    }

    if( failed )
    {
        std::cout << "THERE ARE FAILED TEST CASES\a" << std::endl;
    }

    std::cout << "gpgll " << nmea::gpgll( 10, 10 ) << std::endl;
    std::cout << "gpgga " << nmea::gpgga( 10, 10 ) << std::endl;
    std::cout << "gpgsa " << nmea::gpgsa( ) << std::endl;
    std::cout << "gprmc " << nmea::gprmc( 10, 10, 10, 10 ) << std::endl;
    std::cout << "gpgga_gpgsa_gprmc " << nmea::gpgga_gpgsa_gprmc( 10, 10, 10, 10 ) << std::endl;

    return 0;
}
