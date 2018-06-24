"""Generation of some NMEA senteces, mostly simulated
Based on data from:
http://lefebure.com/articles/nmea-gga/
http://aprs.gids.nl/nmea/
"""

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

def finalize_sentence( sentence ):
    """Wrap NMEA sentence in $ and * characters, and calculate checksum."""
    return "${sentence}*{checksum}".format( sentence=sentence,
                                            checksum=checksum( sentence ) )

def utc_time_str( ):
    """Returns time str for current UTC time: HHMMSS."""
    import time
    return time.strftime( "%H%M%S", time.gmtime( ) )

def date_str( ):
    """Returns date str: DDMMYY."""
    import time
    return time.strftime( "%d%m%y", time.gmtime( ) )

def coord_to_nmea( coord, hemispheres, deg_digits=2 ):
    """Convert floating point number into nmea coord string.
    Takes coordinate itself, string with two character - positive and negative hemi character,
    and how many digit are supposed to be for degrees. For latitude its 2, for longitude it's 3."""
    hemisphere = hemispheres[0] if coord >= 0 else hemispheres[1]
    coord = abs( coord )
    degrees = int( coord )
    minutes = (coord-degrees) / (1/60)
    format_str = "{deg:0" + str( deg_digits ) + "}{min:07.4f},{hemi}"
    return format_str.format( deg=degrees, min=minutes, hemi=hemisphere )

def lat_to_nmea( lat ):
    """Takes latitude in form of double, positive one means North hemisphere, negative - South.
    Returns string in NMEA format - degrees, minutes and hemisphere letter."""
    return coord_to_nmea( lat, "NS" )

def lng_to_nmea( lng ):
    """Takes longitude in form of double, positive one means East hemisphere, negative - West.
    Returns string in NMEA format - degrees, minutes and hemisphere letter."""
    return coord_to_nmea( lng, "EW", 3 )

def gpgll( lat, lng ):
    """Takes geographical coordinates in form of two doubles - latitude and longitude.
    Positive values mean North and East hemispheres, negative - South and West ones.
    Returns string with GPGLL NMEA sentence - Geographic Position, Latitude and Longitude."""
    gpgll_sentence = "GPGLL,{lat},{lng}".format( lat=lat_to_nmea( lat),
                                                 lng=lng_to_nmea( lng ) )
    return finalize_sentence( gpgll_sentence )

def gpgga( lat, lng ):
    """Returns simulated GPGGA sentence - GPS fix data. Similar to GPGLL,
    many arguments are kinda right - faked/simulated."""

    # long version format string, in case you have more data
    # gpgga_sentence="GPGGA,{time},{lat},{lng},{fix},{sat},{prec},{elev},M,{geoid},M,{corr_age},{corr_stat}".format(
    #     time = utc_time_str(), lat = lat_to_nmea( lat ), lng = lng_to_nmea( lng ), fix = 1,
    #     sat = 5, prec = 0.9, elev = 0, geoid = 0, corr_age = "01", corr_stat = "0000" )
    gpgga_sentence="GPGGA,{time},{lat},{lng},1,5,0.9,0,M,0,M,01,0000".format(
        time = utc_time_str(), lat = lat_to_nmea( lat ), lng = lng_to_nmea( lng ) )
    return finalize_sentence( gpgga_sentence )

def gpgsa( ):
    """Faked (simulated) GPGSA sentence - GPS DOP and active satellites."""
    return "$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30"

def gprmc( lat, lng ):
    """Returns faked (simulated) GPRMC sentence - Recommended minimum specific GPS/Transit data.
    Most of its data is faked or, if you will, simulated. :)"""
    gprmc_sentence = "GPRMC,{time},A,{lat},{lng},{speed},{course},{date},000.0,W".format(
        time=utc_time_str( ), lat=lat_to_nmea( lat ), lng=lng_to_nmea( lng ),
        speed = 10.0, course=0.0,
        date=date_str( ) )
    return finalize_sentence( gprmc_sentence )

def selftest():
    from testing import test_returns

    print( __file__, __doc__, "doing self-testing", sep="\n" )

    failed_cases = 0

    test_cases = (
        ( lat_to_nmea, 0, "0000.0000,N" ),
        ( lat_to_nmea, 30, "3000.0000,N" ),
        ( lat_to_nmea, 30.211, "3012.6600,N" ),
        ( lat_to_nmea, -30.211, "3012.6600,S" ),

        ( lng_to_nmea, 0, "00000.0000,E" ),
        ( lng_to_nmea, 30, "03000.0000,E" ),
        ( lng_to_nmea, 30.211, "03012.6600,E" ),
        ( lng_to_nmea, -30.211, "03012.6600,W" ),
        ( lng_to_nmea, -89, "08900.0000,W" ),

        ( gpgll, (0, 0), "$GPGLL,0000.0000,N,00000.0000,E*6B" ),
    )

    failed_cases += test_returns( test_cases )

    if failed_cases:
        print( "selftest: THERE ARE FAILED CASES\a" )
    else:
        print( "selftest: ok" )

if __name__ == "__main__":
    selftest()
