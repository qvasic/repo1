#ifndef NMEA_H_ASDOIFUHASDOFIUASH0897HS08FHDOSDIUFHE05J
#define NMEA_H_ASDOIFUHASDOFIUASH0897HS08FHDOSDIUFHE05J

/*
Generation of some NMEA senteces, mostly simulated
Based on data from:
http://lefebure.com/articles/nmea-gga/
http://aprs.gids.nl/nmea/
*/

namespace nmea
{

std::string checksum( const std::string& sentence );
std::string finalize_sentence( const std::string& sentence );
std::string utc_time_str( );
std::string utc_date_str( );

std::string lat_to_nmea_str( double lat );
std::string lng_to_nmea_str( double lat );

std::string gpgll( double lat, double lng );
std::string gpgga( double lat, double lng );
std::string gpgsa( );
std::string gprmc( double lat, double lng, double speed, double course );
std::string gpgga_gpgsa_gprmc( double lat, double lng, double speed, double course );

}

#endif // NMEA_H
