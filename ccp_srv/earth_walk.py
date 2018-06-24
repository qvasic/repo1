"""Earth walk
This module and routines from it answer basic qestion:
given my current location is N degrees latitude and M degrees longitude,
if I walk/drive/ride/fly D meters in direction D degrees,
what my new location and bearing will be?
WARNING! This module assumes planet you're walking is spherical, real planets aren't!
"""

import math

# mean Earth radius in meters, taken from https://en.wikipedia.org/wiki/Earth
Earth_radius = 6371000

def Earth_dist_to_deg( dist ):
    """Converts meters on Earth's surface into degrees of angle, relative to Earth's center."""
    return rad_to_deg( dist/Earth_radius )

def deg_to_Earth_dist( deg ):
    """Converts degrees of angle, relative to Earth's center, into meters on Earth's surface."""
    return deg_to_rad( deg ) * Earth_radius

def rad_to_deg( r ):
    """Converts radians to degress."""
    return r / ( math.pi/180 )

def deg_to_rad( d ):
    """Converts degrees to radiands."""
    return d * ( math.pi/180 )

def angle( x, y ):
    """Returns angle in degrees between line (0,0)-(x,y) and positive direction of axis X.
    Returned value can be [0, 360)."""

    if x==0:
        if y==0:
            raise ValueError( "No angle can be computed: (0,0)-(0,0) does not define a line." )
        else:
            return 90 if y>0 else 270

    a = rad_to_deg( math.atan( y/x ) )
    if x<0:
        return 180+a
    elif y<0:
        return 360+a
    else:
        return a

def length( x, y ):
    """Returns length of vector (0,0)-(x,y)."""
    return math.sqrt( x**2 + y**2 )

def coords( a, l ):
    """Returns tuple with coordinates of the point, which is located at distance l from origin,
    and at l degrees of angle relative positive direction of axis X."""

    x = math.cos( deg_to_rad( a ) ) * l
    y = math.sin( deg_to_rad( a ) ) * l
    return x, y

def rotate( x, y, a ):
    """Returns coordinates x,y rotated by a degrees around origin.
    Positive a means rotation clockwise, negative - counterclockwise."""
    return coords( angle( x, y )+a, length( x, y ) )

def geo_to_ecef( lat, lng ):
    """Converts geographic coordinates (latitude and longitude) into
    earth-centered, earth-fixed coordinates - (ECEF, three dimentions, XYX).
    Z axis goes from Earth center through north pole,
    X - from center through the point of intersection of prime meridian and equator,
    Y - from center through the point with geographic coordinates 0 degrees lat, 90 degrees lng.
    Assumes radius of the planet as 1, multiply if needed."""

    z = math.sin( deg_to_rad( lat ) )
    xy_plane_projection = math.cos( deg_to_rad( lat ) )
    x = math.cos( deg_to_rad( lng ) ) * xy_plane_projection
    y = math.sin( deg_to_rad( lng ) ) * xy_plane_projection
    return x, y, z

def ecef_to_geo( x, y, z ):
    """Converts ECEF coordinates to geographic ones. See geo_to_ecef for their definitions."""
    if x == 0 and y == 0:
        return ( 90, 0 ) if z > 0 else ( -90, 0 )

    lng = angle( x, y )
    if lng > 180:
        lng -= 360
    lat = angle( length( x, y ), z )
    if lat > 90:
        lat -= 360
    return lat, lng

def step( lat, lng, brng, dist ):
    """Returns new coordinates, if your coordinates were lat, lng
    and moved stright dst degrees (can be calculated from desired distance
    on the surface of the planet - one rad is one radius) in the compass direction brng.
    Done basically by recalculating coordinges with different origins - rotations."""

    if lat == 90 or lat == -90:
        raise ValueError( "There is no one direction to north while being on a pole." )

    x, y, z = geo_to_ecef( 90-dist, 180-brng )
    x, z = rotate( x, z, lat-90 )
    x, y = rotate( x, y, lng )
    return ecef_to_geo( x, y, z )

def dist_and_brng( lat1, lng1, lat2, lng2 ):
    """Returns distance and bearing from point first point to second one.
    Done almost the same, as step( )."""

    if lat1 == lat2 and lng1 == lng2:
        raise ValueError( "Points are the same, there cannot be a direction." )

    if lat1 == 90 or lat1 == -90:
        raise ValueError( "There is no one direction to north while being on a pole." )

    if lat1 == -lat2 and abs( lng1-lng2 ) == 180:
        raise ValueError( "Both points are opposite to each other, there is no one direction between them." )

    x, y, z = geo_to_ecef( lat2, lng2 )
    x, y = rotate( x, y, -lng1 )
    x, z = rotate( x, z, 90-lat1 )
    r_dist, r_brng = ecef_to_geo( x, y, z )

    return 90-r_dist, 180-r_brng


################################################################################

def walk_shit():
    cp = (0,0)
    cb = 45
    steps = 3600000

    for i in range( steps ):
        pp = cp
        cp = step( *cp, cb, 360/steps )
        cb = ( dist_and_brng( *cp, *pp )[1]+180 ) % 360
        print( "{:.10f} {:.10f} {:.10f}".format( *cp, cb ) )

def selftest():
    print( __file__, __doc__, "doing self-testing", sep="\n" )

    from testing import test_returns, test_raises, CompareFloatSeq

    failed = 0
    float_seq_cmp = CompareFloatSeq( 12 )
    cos_45 = math.cos( math.pi/4 )

    ret_cases = (
        ( angle, (1,0),     0 ),
        ( angle, (1,1),     45 ),
        ( angle, (0,1),     90 ),
        ( angle, (-1,1),    135 ),
        ( angle, (-1,0),    180 ),
        ( angle, (-1,-1),   225 ),
        ( angle, (0,-1),    270 ),
        ( angle, (1,-1),    315 ),

        ( length, (1,0),    1 ),
        ( length, (0,-2),   2 ),
        ( length, (cos_45, cos_45), 1 ),
        ( length, (1,2),    2.23606797749979 ),

        ( coords, (0, 1),   (1, 0),     float_seq_cmp ),
        ( coords, (45, 1),  (cos_45, cos_45), float_seq_cmp ),
        ( coords, (90, 1),  (0, 1),     float_seq_cmp ),
        ( coords, (180, 1), (-1, 0),    float_seq_cmp ),
        ( coords, (270, 1), (0, -1),    float_seq_cmp ),
        ( coords, (315+720, 1), (cos_45, -cos_45), float_seq_cmp ),

        ( rotate, ( 1, 0, 90 ), ( 0, 1 ), float_seq_cmp ),
        ( rotate, ( 0, 1, -90 ), ( 1, 0 ), float_seq_cmp ),
        ( rotate, ( 2, 0, 45 ), (2*cos_45, 2*cos_45 ), float_seq_cmp ),
        ( rotate, ( 2, 0, -45 ), (2*cos_45, -2*cos_45 ), float_seq_cmp ),

        ( geo_to_ecef, ( 0, 0 ), ( 1, 0, 0 ) ),
        ( geo_to_ecef, ( 0, 90 ), ( 0, 1, 0 ), float_seq_cmp ),
        ( geo_to_ecef, ( 90, 0 ), ( 0, 0, 1 ), float_seq_cmp ),
        ( geo_to_ecef, ( 90, 180 ), ( 0, 0, 1 ), float_seq_cmp ),
        ( geo_to_ecef, ( 90, 213 ), ( 0, 0, 1 ), float_seq_cmp ),
        ( geo_to_ecef, ( 45, 90 ), ( 0, cos_45, cos_45 ), float_seq_cmp ),
        ( geo_to_ecef, ( 45, 180 ), ( -cos_45, 0, cos_45 ), float_seq_cmp ),
        ( geo_to_ecef, ( -45, 180 ), ( -cos_45, 0, -cos_45 ), float_seq_cmp ),
        ( geo_to_ecef, ( 45, -90 ), ( 0, -cos_45, cos_45 ), float_seq_cmp ),
        ( geo_to_ecef, ( 45, 45 ), ( cos_45**2, cos_45**2, cos_45 ), float_seq_cmp ),

        ( ecef_to_geo, ( 1, 0, 0 ), ( 0, 0 ) ),
        ( ecef_to_geo, ( 0, 1, 0 ), ( 0, 90 ) ),
        ( ecef_to_geo, ( 0, 0, 1 ), ( 90, 0 ) ),
        ( ecef_to_geo, ( 0, 0, -1 ), ( -90, 0 ) ),
        ( ecef_to_geo, ( -cos_45**2, -cos_45**2, -cos_45 ), ( -45, -135 ) ),

        ( step, ( 0, 0, 0, 45 ), ( 45, 0 ), float_seq_cmp ),
        ( step, ( 0, 45, 0, 10 ), ( 10, 45 ), float_seq_cmp ),
        ( step, ( 0, 45, 270, 10 ), ( 0, 35 ), float_seq_cmp ),

        ( dist_and_brng, ( 0, 0, 0, 45 ), ( 45, 90 ), float_seq_cmp ),
        ( dist_and_brng, ( 0, 0, 0, -5 ), ( 5, 270 ), float_seq_cmp ),
        ( dist_and_brng, ( 10, 0, -10, 0 ), ( 20, 180 ), float_seq_cmp ),
    )

    failed += test_returns( ret_cases )

    exc_cases = (
        ( angle,            (0,0),                  ValueError ),
        ( step,             ( 90, 180, 0, 45 ),     ValueError ),
        ( step,             ( -90, 180, 0, 45 ),    ValueError ),
        ( dist_and_brng,    ( 90, 0, 0, 0 ),        ValueError ),
        ( dist_and_brng,    ( -90, 0, 0, 0 ),       ValueError ),
        ( dist_and_brng,    ( 10, 10, 10, 10 ),     ValueError ),
        ( dist_and_brng,    ( -10, 10, 10, -170 ),  ValueError ),
        ( dist_and_brng,    ( -10, -30, 10, 150 ),  ValueError ),
    )
    failed += test_raises( exc_cases )

    if failed:
        print( "\nselftest: THERE ARE {} FAILED CASES\a\n".format( failed ) )
    else:
        print( "\nselftest: ok\n" )

    walk_shit()

if __name__ == "__main__":
    selftest()
