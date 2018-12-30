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

    assert dist >= 0

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

import unittest
cos_45 = math.cos( math.pi/4 )

class EarthWalkUnitTests ( unittest.TestCase ):
    def __init__( self, second ):
        unittest.TestCase.__init__( self, second )
        self.AlmostEqual_places = 12

    def assertSequenceAlmostEqual( self, seq1, seq2, places=None, msg=None, delta=None ):
        """Compares sequences, each element is rounded before comparing."""
        if places is not None and "AlmostEqual_places" in self.__dict__:
            places = self.AlmostEqual_places
        for elem1, elem2 in zip( seq1, seq2 ):
            self.assertAlmostEqual( elem1, elem2, places=places, msg=msg, delta=delta )

    def test_angle( self ):
        self.assertEqual( angle( 1, 0 ), 0 )
        self.assertEqual( angle( 1, 0 ), 0 )
        self.assertEqual( angle( 1, 1 ), 45 )
        self.assertEqual( angle( 0, 1 ), 90 )
        self.assertEqual( angle( -1, 1 ), 135 )
        self.assertEqual( angle( -1, 0 ), 180 )
        self.assertEqual( angle( -1, -1 ), 225 )
        self.assertEqual( angle( 0, -1 ), 270 )
        self.assertEqual( angle( 1, -1 ), 315 )

        self.assertRaises( ValueError, angle, 0, 0 )

    def test_length( self ):
        self.assertEqual( length( 0, 0 ), 0 )
        self.assertEqual( length( 1, 0 ), 1 )
        self.assertEqual( length( 0, -2 ), 2 )
        self.assertEqual( length( cos_45, cos_45 ), 1 )
        self.assertEqual( length( 1, 2 ), 2.23606797749979 )

    def test_coords( self ):
        self.assertEqual( coords( 0, 1 ), (1, 0) )
        self.assertSequenceAlmostEqual( coords( 45, 1 ), (cos_45, cos_45) )
        self.assertSequenceAlmostEqual( coords( 90, 1 ), (0, 1) )
        self.assertSequenceAlmostEqual( coords( 180, 1 ), (-1, 0) )
        self.assertSequenceAlmostEqual( coords( 270, 1 ), (0, -1) )
        self.assertSequenceAlmostEqual( coords( 315+720, 1 ), (cos_45, -cos_45) )

    def test_rotate( self ):
        self.assertSequenceAlmostEqual( rotate( 1, 0, 0 ), ( 1, 0 ) )
        self.assertSequenceAlmostEqual( rotate( 1, 0, 90 ), ( 0, 1 ) )
        self.assertSequenceAlmostEqual( rotate( 0, 1, -90 ), ( 1, 0 ) )
        self.assertSequenceAlmostEqual( rotate( 2, 0, 45 ), (2*cos_45, 2*cos_45 ) )
        self.assertSequenceAlmostEqual( rotate( 2, 0, -45 ), (2*cos_45, -2*cos_45 ) )

    def test_geo_to_ecef( self ):
        self.assertSequenceAlmostEqual( geo_to_ecef( 0, 0 ), ( 1, 0, 0 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( 0, 90 ), ( 0, 1, 0 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( 90, 0 ), ( 0, 0, 1 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( 90, 180 ), ( 0, 0, 1 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( 90, 213 ), ( 0, 0, 1 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( 45, 90 ), ( 0, cos_45, cos_45 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( 45, 180 ), ( -cos_45, 0, cos_45 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( -45, 180 ), ( -cos_45, 0, -cos_45 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( 45, -90 ), ( 0, -cos_45, cos_45 ) )
        self.assertSequenceAlmostEqual( geo_to_ecef( 45, 45 ), ( cos_45**2, cos_45**2, cos_45 ) )

    def test_ecef_go_geo( self ):
        self.assertSequenceAlmostEqual( ecef_to_geo( 1, 0, 0 ), ( 0, 0 ) )
        self.assertSequenceAlmostEqual( ecef_to_geo( 0, 1, 0 ), ( 0, 90 ) )
        self.assertSequenceAlmostEqual( ecef_to_geo( 0, 0, 1 ), ( 90, 0 ) )
        self.assertSequenceAlmostEqual( ecef_to_geo( 0, 0, -1 ), ( -90, 0 ) )
        self.assertSequenceAlmostEqual( ecef_to_geo( -cos_45**2, -cos_45**2, -cos_45 ),
                                        ( -45, -135 ) )

    def test_step( self ):
        self.assertSequenceAlmostEqual( step( 0, 0, 0, 45 ), ( 45, 0 ) )
        self.assertSequenceAlmostEqual( step( 0, 45, 0, 10 ), ( 10, 45 ) )
        self.assertSequenceAlmostEqual( step( 0, 45, 270, 10 ), ( 0, 35 ) )
        self.assertSequenceAlmostEqual( step( 0, 0, 30, 90 ), ( 60, 90 ) )
        self.assertSequenceAlmostEqual( step( 30, -90, 90, 90 ), ( 0, 0 ) )
        self.assertRaises( ValueError, step, 90, 180, 0, 45 )
        self.assertRaises( ValueError, step, -90, 180, 0, 45 )


    def test_dist_and_brng( self ):
        self.assertSequenceAlmostEqual( dist_and_brng( 0, 0, 0, 45 ), ( 45, 90 ) )
        self.assertSequenceAlmostEqual( dist_and_brng( 0, 0, 0, -5 ), ( 5, 270 ) )
        self.assertSequenceAlmostEqual( dist_and_brng( 10, 0, -10, 0 ), ( 20, 180 ) )
        self.assertRaises( ValueError, dist_and_brng, 90, 0, 0, 0 )
        self.assertRaises( ValueError, dist_and_brng, -90, 0, 0, 0 )
        self.assertRaises( ValueError, dist_and_brng, 10, 10, 10, 10 )
        self.assertRaises( ValueError, dist_and_brng, -10, 10, 10, -170 )
        self.assertRaises( ValueError, dist_and_brng, -10, -30, 10, 150 )

if __name__ == "__main__":
    unittest.main( )

