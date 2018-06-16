#ifndef COMMON_H_SADFHSAD08F7HASD98F7HAS9D8FHSA9D8F7HAS9D8F7H
#define COMMON_H_SADFHSAD08F7HASD98F7HAS9D8FHSA9D8F7HAS9D8F7H

#include <arpa/inet.h>

inline constexpr uint32_t make_ip_addr( uint8_t B1, uint8_t B2, uint8_t B3, uint8_t B4 )
{
    return static_cast<uint32_t>( B4 )<<24
         | static_cast<uint32_t>( B3 )<<16
         | static_cast<uint32_t>( B2 )<<8
         | static_cast<uint32_t>( B1 );
}

inline std::ostream &operator<<( std::ostream &os, const in_addr &a )
{
    /*os << ( a.s_addr&0xff )     << '.' << ( a.s_addr>>8&0xff ) << '.'
       << ( a.s_addr>>16&0xff ) << '.' << ( a.s_addr>>24 );*/
    os << inet_ntoa( a );
    return os;
}

#endif // COMMON_H
