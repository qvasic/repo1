import unittest

def position_polyline( polyline, orient=(0,-1), posit=(0,0) ):
    import pygame.math
    angle = -pygame.math.Vector2( orient ).angle_to( (0, -1) )
    return [ [ rot+rel for rot, rel in zip( pygame.math.Vector2( p ).rotate( angle ), posit ) ]
             for p in polyline ]

def rotate_vec( vec, orient, posit=(0,0) ):
    import pygame.math
    angle = -pygame.math.Vector2( orient ).angle_to( (0, -1) )
    return tuple( r+p for r, p in zip( pygame.math.Vector2( vec ).rotate( angle ), posit ) )

def length( v ):
    """Return length of the vector v."""
    import math
    return math.sqrt( v[0]**2 + v[1]**2 )

def redirect_vec( v_from, v_to ):
    """Redirects vector v_from in the direction of v_to.
    Basically it builds new vector of length of v_from in the direction v_to."""
    coef = length( v_from )/length( v_to )
    return [ c*coef for c in v_to ]

def apply_threshold( seq, threshold ):
    """Apply threshold to sequence seq. If an absolute value of an element is less then threshold - then it becomes 0,
    otherwise value is returned unchanged."""
    less_than_threshold = True
    for val in seq:
        if abs( val ) >= threshold:
            return seq
    else:
        return ( 0, ) * len( seq )

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Point( {}, {} )".format( self.x, self.y )

    def __repr__(self):
        return self.__str__( );

    def __eq__(self, other):
        return type( other ) is Point and self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

class Line:
    def __init__(self, p1, p2):
        assert( p1 != p2 )

        if p1.x == p2.x:
            self.vertical = True
            self.x = p1.x
        else:
            self.vertical = False
            self.a = ( p1.y - p2.y ) / ( p1.x - p2.x )
            self.b = p1.y - p1.x * self.a

    def __eq__(self, other):
        if type( other ) is not Line:
            return False

        if self.vertical != other.vertical:
            return False

        if self.vertical:
            return self.x == other.x
        else:
            return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self == other

class Circle:
    def __init__( self, center, radius ):
        assert( radius > 0 )
        self.center = center
        self.radius = radius

    def __eq__(self, other):
        return type( other ) is Circle and self.center == other.center and self.radius == other.radius

    def __ne__(self, other):
        return not self == other


def is_point_on_line( line, point ):
    assert( type( line ) is Line )
    assert( type( point ) is Point )

    if line.vertical:
        return point.x == line.x

    return point.x * line.a + line.b == point.y


def intersect_lines( line1, line2 ):
    """Calculates point of intersection of two lines.
    If lines do not intersect - returns None.
    If line do intersect - return point object with value of point of intersection.
    If lines are the same - meaning there are infinite number of points of intersection - returns float( "Infinity" ).
    """
    assert( type( line1 ) is Line )
    assert( type( line2 ) is Line )

    if line1 == line2:
        return float( "Infinity" )

    if line1.vertical and line2.vertical:
        # x-s are not equal because line1 != line2
        return None

    if not line1.vertical and not line2.vertical and line1.a == line2.a:
        # b-s are not equal because line1 != line2
        return None

    if line2.vertical:
        # only one might be vertical because we checked that above
        line1, line2 = line2, line1

    if line1.vertical:
        # one is vertical two is not
        return Point( line1.x, line2.a * line1.x + line2.b )
    else:
        # both is not vertical
        x = ( line2.b - line1.b ) / ( line1.a - line2.a )
        return Point( x, line1.a * x + line1.b )

def intersect_line_and_circle( circle, line ):
    assert( type( line ) is Line )
    assert( type( circle ) is Circle )

    from math import sqrt

    def asdfasdfsadfasdfsdf( line, point, dist ):
        if line.vertical:
            return ( Point( line.x, point.y + dist ), Point( line.x, point.y - dist ) )

        x_span = dist / sqrt( 1 + line.a ** 2 )

        return ( Point( point.x + x_span, line.a * (point.x + x_span ) + line.b ),
                 Point( point.x - x_span, line.a * (point.x - x_span ) + line.b ) )

    if is_point_on_line( line, circle.center ):
        # line goes through circle.center
        return asdfasdfsadfasdfsdf( line, circle.center, circle.radius )

    # more general case: create perpendicular to line that goes through circle.center
    perpendicular = Line( Point( 0, 0 ), Point( 0, 1 ) )
    if line.vertical:
        perpendicular.vertical = False
        perpendicular.a = 0
        perpendicular.b = circle.center.y
    elif line.a == 0:
        perpendicular.x = circle.center.x
    else:
        perpendicular.vertical = False
        perpendicular.a = -1 / line.a
        perpendicular.b = perpendicular.a * circle.center.x - circle.center.y

    closest_point = intersect_lines( line, perpendicular )
    distance_to_closest_point = math.sqrt( ( closest_point.x - circle.center.x ) ** 2
                                           + ( closest_point.y - circle.center.y ) ** 2 )

    if distance_to_closest_point > circle.radius:
        return None
    elif distance_to_closest_point == circle.radius:
        return closest_point
    else:
        pass
        # general case: two points


class TestPolylineProximityRoutines( unittest.TestCase ):
    def test_point_eq_ne_operators( self ):
        self.assertTrue( Point( 1, 1 ) == Point( 1, 1 ) )
        self.assertFalse( Point( 1, 1 ) == Point( 1, 1.01 ) )
        self.assertFalse( Point( 1, 1 ) == Point( 1.1, 1 ) )

        self.assertFalse( Point( 1, 1 ) != Point( 1, 1 ) )
        self.assertTrue( Point( 1, 1 ) != Point( 1, 1.01 ) )
        self.assertTrue( Point( 1, 1 ) != Point( 1.1, 1 ) )

        self.assertFalse( Point( 1, 1 ) == 20 )
        self.assertTrue( Point( 1, 1 ) != "abra" )

    def test_line_eq_ne_operators( self ):
        self.assertTrue( Line( Point( 10, 0 ), Point( 10, 10 )  ) == Line( Point( 10, 0 ), Point( 10, 10 ) ) )
        self.assertFalse( Line( Point( 10, 0 ), Point( 10, 10 )  ) == Line( Point( 9, 0 ), Point( 9, 10 ) ) )

        self.assertFalse( Line( Point( 10, 0 ), Point( 11, 1 )  ) == Line( Point( 10, 0 ), Point( 10, 10 ) ) )

        self.assertTrue( Line( Point( 10, 0 ), Point( 11, 1 )  ) == Line( Point( 12, 2 ), Point( 10, 0 ) ) )
        self.assertFalse( Line( Point( 10, 0 ), Point( 11, 1 )  ) == Line( Point( 12, 2 ), Point( 10, 0.2 ) ) )
        self.assertFalse( Line( Point( 10, 0 ), Point( 11, 1 )  ) == Line( Point( 10, 1 ), Point( 11, 2 ) ) )

        self.assertFalse( Line( Point( 10, 0 ), Point( 10, 10 )  ) != Line( Point( 10, 0 ), Point( 10, 10 ) ) )
        self.assertTrue( Line( Point( 10, 0 ), Point( 10, 10 )  ) != Line( Point( 9, 0 ), Point( 9, 10 ) ) )

        self.assertTrue( Line( Point( 10, 0 ), Point( 11, 1 )  ) != Line( Point( 10, 0 ), Point( 10, 10 ) ) )

        self.assertFalse( Line( Point( 10, 0 ), Point( 11, 1 )  ) != Line( Point( 12, 2 ), Point( 10, 0 ) ) )
        self.assertTrue( Line( Point( 10, 0 ), Point( 11, 1 )  ) != Line( Point( 12, 2 ), Point( 10, 0.2 ) ) )
        self.assertTrue( Line( Point( 10, 0 ), Point( 11, 1 )  ) != Line( Point( 10, 1 ), Point( 11, 2 ) ) )

        self.assertFalse(Line(Point(10, 0), Point(11, 1)) == Point( 1, 1 ) )
        self.assertTrue(Line(Point(10, 0), Point(11, 1)) != Circle( Point( 0, 0 ), 2 ) )

    def test_circle_eq_ne_operators( self ):
        self.assertTrue( Circle( Point( 10, 10 ), 10 ) == Circle( Point( 10, 10 ), 10 ) )

        self.assertFalse( Circle( Point( 10, 10 ), 10 ) == Circle( Point( 10, 10.1 ), 10 ) )
        self.assertFalse( Circle( Point( 10, 10 ), 10 ) == Circle( Point( 10, 10 ), 9.9 ) )

        self.assertFalse( Circle( Point( 10, 10 ), 10 ) != Circle( Point( 10, 10 ), 10 ) )

        self.assertTrue( Circle( Point( 10, 10 ), 10 ) != Circle( Point( 10, 10.1 ), 10 ) )
        self.assertTrue( Circle( Point( 10, 10 ), 10 ) != Circle( Point( 10, 10 ), 9.9 ) )

        self.assertFalse(Circle(Point(10, 10), 10) == 0.0 )
        self.assertTrue(Circle(Point(10, 10), 10) != None)

    def test_valid_line(self):
        l = Line( Point( 0, 0 ), Point( 1, 0 ) )
        self.assertEqual( l.vertical, False )
        self.assertEqual( l.a, 0 )
        self.assertEqual( l.b, 0 )

        l = Line( Point( 0, 0 ), Point( 1, 1 ) )
        self.assertEqual( l.vertical, False )
        self.assertEqual( l.a, 1 )
        self.assertEqual( l.b, 0 )

        l = Line( Point( 0, 2 ), Point( 2, 1 ) )
        self.assertEqual( l.vertical, False )
        self.assertEqual( l.a, -0.5 )
        self.assertEqual( l.b, 2 )

        l = Line( Point( 1, 2 ), Point( 2, 1 ) )
        self.assertEqual( l.vertical, False )
        self.assertEqual( l.a, -1 )
        self.assertEqual( l.b, 3 )

        l = Line( Point( 10, 2 ), Point( 10, 10 ) )
        self.assertEqual( l.vertical, True )
        self.assertEqual( l.x, 10 )

    def test_invalid_line(self):
        with self.assertRaises( AssertionError ):
            Line( Point( 0, 0 ), Point( 0, 0 ) )

    def test_invalid_circle(self):
        with self.assertRaises( AssertionError ):
            Circle( Point( 0, 0 ), -10 )

        with self.assertRaises( AssertionError ):
            Circle( Point( 0, 0 ), 0 )

    def test_is_point_on_line( self ):
        self.assertTrue( is_point_on_line( Line( Point( 0, 0 ), Point( 0, 10 ) ), Point( 0, 0 ) ) )
        self.assertFalse( is_point_on_line( Line( Point( 0, 0 ), Point( 0, 10 ) ), Point( 0.1, 0 ) ) )
        self.assertTrue( is_point_on_line( Line( Point( 0, 0 ), Point( 10, 10 ) ), Point( 1, 1 ) ) )
        self.assertFalse( is_point_on_line( Line( Point( 0, 0 ), Point( 10, 10 ) ), Point( 1, 2 ) ) )

    def test_intersect_lines( self ):
        self.assertEqual( intersect_lines( Line( Point( 0, 0 ), Point( 0, 10 ) ),
                                           Line( Point( 0, 5 ), Point( 0, 5.1 ) ) ),
                          float( "Infinity" ) )
        self.assertEqual( intersect_lines( Line( Point( 1, 1 ), Point( 10, 10 ) ),
                                           Line( Point( 0, 0 ), Point( -1, -1 ) ) ),
                          float( "Infinity" ) )

        self.assertEqual( intersect_lines( Line( Point( 1, 1 ), Point( 1, 10 ) ),
                                           Line( Point( 0, 0 ), Point( 0, -1 ) ) ),
                          None )
        self.assertEqual( intersect_lines( Line( Point( 1, 1 ), Point( 10, 10 ) ),
                                           Line( Point( 0, 1 ), Point( -1, 0 ) ) ),
                          None )

        self.assertEqual( intersect_lines( Line( Point( 10, 1 ), Point( 10, 10 ) ),
                                           Line( Point( 0, 1 ), Point( -1, 0 ) ) ),
                          Point( 10, 11 ) )
        self.assertEqual( intersect_lines( Line( Point( 0, 1 ), Point( -1, 0 ) ),
                                           Line( Point( 10, 1 ), Point( 10, 10 ) ) ),
                          Point( 10, 11 ) )

        self.assertEqual( intersect_lines( Line( Point( 0, 0 ), Point( -1, -1 ) ),
                                           Line( Point( 2, 0 ), Point( 0, 2 ) ) ),
                          Point( 1, 1 ) )


    def test_intersect_line_and_circle( self ):
        self.assertEqual( intersect_line_and_circle( Circle( Point( 0, 0 ), 10 ),
                                                     Line( Point( 0, 0 ), Point( 0, -1 ) ) ),
                          ( Point( 0, 10 ), Point( 0, -10 ) ) )
        self.assertEqual( intersect_line_and_circle( Circle( Point( 0, 0 ), 10 ),
                                                     Line( Point( 0, 0 ), Point( -1, -1 ) ) ),
                          ( Point( 7.071067811865475, 7.071067811865475 ),
                            Point( -7.071067811865475, -7.071067811865475 ) ) )
        self.assertEqual( intersect_line_and_circle( Circle( Point( 0, 1 ), 10 ),
                                                     Line( Point( -10, 1 ), Point( 1, 1 ) ) ),
                          ( Point( 10, 1 ), Point( -10, 1 ) ) )


if __name__ == "__main__":
    unittest.main( )
