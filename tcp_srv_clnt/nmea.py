"""FORMAT OF COORDINATES STRINGS STILL UNVERIFIED!!!!
consult http://lefebure.com/articles/nmea-gga/ and http://aprs.gids.nl/nmea/
https://docs.python.org/3.4/library/string.html#grammar-token-width
also implement
GPGGA Global Positioning System Fix Data
GPGSA GPS DOP and active satellites
GPRMC Recommended minimum specific GPS/Transit data
\a"""
print( __doc__ )

def checksum( nmea_sentence ):
    """Calculates proper NMEA checksum.
    Expects all characters in nmea_sentence to be ASCII characters.
    Basically xores all characters together and returns hex digits of the results."""
    checksum = 0
    for c in nmea_sentence:
        checksum ^= ord( c )
    hex_digits = hex( checksum )[2:]
    if len( hex_digits ) == 1:
        hex_digits = '0'+hex_digits
    return hex_digits.upper()

def coord_to_nmea( coord, hemispheres ):
    import math
    hemisphere = hemispheres[0] if coord >= 0 else hemispheres[1]
    coord = abs( coord )
    degrees = math.floor( coord )
    minutes = round( (coord-degrees) / (1/60), 2 )
    return "{deg:03}{min},{hemi}".format( deg=degrees, min=minutes, hemi=hemisphere )

def lat_to_nmea( lat ):
    """Takes latitude in form of double, positive one means North hemisphere, negative - South.
    Returns string in NMEA format - degrees, minutes and hemisphere letter."""
    return coord_to_nmea( lat, "NS" )

def lng_to_nmea( lng ):
    """Takes longitude in form of double, positive one means East hemisphere, negative - West.
    Returns string in NMEA format - degrees, minutes and hemisphere letter."""
    return coord_to_nmea( lng, "EW" )

def gpgll( lat, lng ):
    """Takes geographical coordinates in form of two doubles - latitude and longitude.
    Positive values mean North and East hemispheres, negative - South and West ones.
    Returns string with GPGLL NMEA sentence - Geographic Position, Latitude and Longitude."""
    gpgll_sentence = "GPGLL,{lat},{lng}".format( lat=lat_to_nmea( lat),
                                                 lng=lng_to_nmea( lng ) )
    return "${sentence}*{checksum}".format( sentence=gpgll_sentence,
                                            checksum=checksum( gpgll_sentence ) )

def test_one( func, cases ):
    failed = 0
    for param, expected in cases:
        if type( param ) is tuple:
            actual = func( *param )
        else:
            actual = func( param )
        if actual != expected:
            print( "{f}( {p} ) retuned {a}, while {e} was expected".format(
                               f=func.__name__, p=param, a=actual, e=expected ) )
            failed += 1
    return failed

def selftest():
    failed_cases = 0

    latitude_cases = (
        ( 0, "00.0,N" ),
        ( 30, "300.0,N" ),
        ( 30.211, "3012.66,N" ),
        ( -30.211, "3012.66,S" ),
    )
    failed_cases += test_one( lat_to_nmea, latitude_cases )

    longitude_cases = (
        ( 0, "00.0,E" ),
        ( 30, "300.0,E" ),
        ( 30.211, "3012.66,E" ),
        ( -30.211, "3012.66,W" ),
        ( -89, "890.0,W" ),
    )
    failed_cases += test_one( lng_to_nmea, longitude_cases )

    gpgll_cases = (
        ( (0, 0), "$GPGLL,00.0,N,00.0,E*5B" ),
    )

    failed_cases += test_one( gpgll, gpgll_cases )

    if failed_cases:
        print( "selftest: THERE ARE FAILED CASES\a" )
    else:
        print( "selftest: ok" )


if __name__ == "__main__":
    selftest()
