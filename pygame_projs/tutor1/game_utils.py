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

    return tuple( v if abs( v ) >= threshold else 0 for v in seq )

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

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
        self.center = center
        self.radius = radius

def intersect_lines( line1, line2 ):
    """Calculates point of intersection of two lines.
    If lines do not intersect - returns None.
    If line do intersect - return point object with value of point of intersection.
    If lines are the same - meaning there are infinite number of points of intersection - returns float( "Infinity" ).
    """
    assert( type( line1 ) is Line )
    assert( type( line2 ) is Line )

def intersect_line_and_circle( circle, line ):
    assert( type( line ) is Line )
    assert( type( circle ) is Circle )


class TestPolylineProximityRoutines( unittest.TestCase ):
    def test_point_eq_ne_operators( self ):
        self.assertTrue( Point( 1, 1 ) == Point( 1, 1 ) )
        self.assertFalse( Point( 1, 1 ) == Point( 1, 1.01 ) )
        self.assertFalse( Point( 1, 1 ) == Point( 1.1, 1 ) )

    def test_line_eq_ne_operators( self ):
        self.assertTrue( Line( Point( 10, 0 ), Point( 10, 10 )  ) == Line( Point( 10, 0 ), Point( 10, 10 ) ) )
        self.assertFalse( Line( Point( 10, 0 ), Point( 10, 10 )  ) == Line( Point( 9, 0 ), Point( 9, 10 ) ) )

        self.assertFalse( Line( Point( 10, 0 ), Point( 11, 1 )  ) == Line( Point( 10, 0 ), Point( 10, 10 ) ) )

        self.assertTrue( Line( Point( 10, 0 ), Point( 11, 1 )  ) == Line( Point( 12, 2 ), Point( 10, 0 ) ) )
        self.assertFalse( Line( Point( 10, 0 ), Point( 11, 1 )  ) == Line( Point( 12, 2 ), Point( 10, 0.2 ) ) )
        self.assertFalse( Line( Point( 10, 0 ), Point( 11, 1 )  ) == Line( Point( 10, 1 ), Point( 11, 2 ) ) )

    def test_circle_eq_ne_operators( self ):
        self.assertTrue( False )

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

    def test_intersect_lines( self ):
        self.assertTrue( False )

    def test_intersect_line_and_circle( self ):
        self.assertTrue( False )


if __name__ == "__main__":
    unittest.main( )
