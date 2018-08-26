#include <string>
#include <chrono>
#include <ctime>
#include <cmath>

#include "nmea.h"

namespace nmea
{

std::string checksum( const std::string& sentence )
{
    /* Calculates proper NMEA checksum.
    Expects all characters in nmea_sentence to be ASCII characters.
    Basically xores all characters together and returns hex digits of the results. */

    int check = 0;
    for( auto c : sentence )
    {
        check ^= c;
    }

    constexpr size_t bufsize = 10;
    char buffer[bufsize];
    snprintf( buffer, bufsize, "%.2X", check );

    return buffer;
}

std::string finalize_sentence( const std::string& sentence )
{
    /* Wrap NMEA sentence in $ and * characters, and calculates checksum. */

    return "$" + sentence + "*" + checksum( sentence );
}

std::string utc_time_str( )
{
    /* Returns time str for current UTC time: HHMMSS.SS */

    constexpr size_t bufsize = 20;
    char buffer[bufsize] = "";

    auto current_time = std::time( nullptr );
    std::strftime( buffer, bufsize-1, "%H%M%S", std::gmtime( &current_time  ) );

    auto fraction = std::chrono::duration_cast< std::chrono::milliseconds >(
            std::chrono::high_resolution_clock::now( ).time_since_epoch( ) ).count( ) % 1000 / 10;

    std::string fraction_str = ( fraction > 9 ? "." : ".0" ) + std::to_string( fraction );

    return buffer + fraction_str;
}

std::string utc_date_str( )
{
    /* Returns date str: DDMMYY */

    constexpr size_t bufsize = 20;
    char buffer[bufsize] = "";

    auto current_time = std::time( nullptr );
    std::strftime( buffer, bufsize-1, "%d%m%y", std::gmtime( &current_time  ) );

    return buffer;
}

namespace
{

inline std::string coord_to_nmea_str( double lat, const char* hemis, int width = 2 )
{
    /* Convert floating point number into nmea coord string.
    Takes coordinate itself, string with two character - positive and negative hemi character,
    and how many digit are supposed to be for degrees. For latitude its 2, for longitude it's 3. */

    constexpr size_t bufsize = 20;
    char buffer[bufsize] = "";

    char hemi = lat >= 0 ? hemis[0] : hemis[1];
    int deg = std::trunc( std::abs( lat ) );
    auto fraction = ( std::abs( lat ) - deg ) / ( double( 1 )/60 );

    snprintf( buffer, bufsize, "%0*d%07.4f,%c", width, deg, fraction, hemi );

    return buffer;
}

}

std::string lat_to_nmea_str( double lat )
{
    /* Takes latitude in form of double, positive one means North hemisphere, negative - South.
    Returns string in NMEA format - degrees, minutes and hemisphere letter. */

    return coord_to_nmea_str( lat, "NS" );
}

std::string lng_to_nmea_str( double lat )
{
    /* Takes longitude in form of double, positive one means East hemisphere, negative - West.
    Returns string in NMEA format - degrees, minutes and hemisphere letter. */

    return coord_to_nmea_str( lat, "EW", 3 );
}

std::string gpgll( double lat, double lng )
{
    /* Takes geographical coordinates in form of two doubles - latitude and longitude.
    Positive values mean North and East hemispheres, negative - South and West ones.
    Returns string with GPGLL NMEA sentence - Geographic Position, Latitude and Longitude. */

    std::string sentence = "GPGLL," + lat_to_nmea_str( lat ) + "," + lng_to_nmea_str( lng );
    return finalize_sentence( sentence );
}

std::string gpgga( double lat, double lng )
{
    /* Returns simulated GPGGA sentence - GPS fix data. Similar to GPGLL,
    many arguments are "kinda" right - faked/simulated. */

    std::string sentence = "GPGGA," + utc_time_str( ) + ","
                            + lat_to_nmea_str( lat ) + "," + lng_to_nmea_str( lng )
                            + ",1,5,0.9,0,M,0,M,01,0000";
    return finalize_sentence( sentence );
}

std::string gpgsa( )
{
    /* Faked (simulated) GPGSA sentence - GPS DOP and active satellites. */

    return "$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30";
}

std::string gprmc( double lat, double lng, double speed, double course )
{
    /* Returns faked (simulated) GPRMC sentence - Recommended minimum specific GPS/Transit data.
    Most of its data is faked or, if you will, simulated. :) */

    auto meters_to_knots = []( double speed_m ) -> double
    {
        return speed_m/1852;
    };

    constexpr size_t bufsize = 20;
    char buffer[bufsize] = "";
    snprintf( buffer, bufsize, "%.1f,%.1f", meters_to_knots( speed ), course );

    std::string sentence = "GPRMC," + utc_time_str( ) + ",A,"
            + lat_to_nmea_str( lat ) + "," + lng_to_nmea_str( lng )
            + "," + buffer + "," + utc_date_str( ) + ",000.0,W";
    return finalize_sentence( sentence );
}

std::string gpgga_gpgsa_gprmc( double lat, double lng, double speed, double course )
{
    /* Returns newline-separated GPGGA, GPGSA and GPRMC sentences. */

    return gpgga( lat, lng ) + "\n"
           + gpgsa( ) + "\n"
           + gprmc( lat, lng, speed, course ) + "\n";
}

}
