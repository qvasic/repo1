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

class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

class line:
    def __init__(self, p1, p2):
        assert( p1 != p2 )

        if p1.x == p2.x:
            self.vertical = True
            self.x = p1.x
        else:
            self.vertical = False
            self.a = ( p1.y - p2.y ) / ( p1.x - p2.x )
            self.b = p1.y - p1.x * self.a


class TestPolylineProximityRoutines( unittest.TestCase ):
    def test_valid_line(self):
        l = line( point( 0, 0 ), point( 1, 0 ) )
        self.assertEqual( l.vertical, False )
        self.assertEqual( l.a, 0 )
        self.assertEqual( l.b, 0 )

        l = line( point( 0, 0 ), point( 1, 1 ) )
        self.assertEqual( l.vertical, False )
        self.assertEqual( l.a, 1 )
        self.assertEqual( l.b, 0 )

        l = line( point( 0, 2 ), point( 2, 1 ) )
        self.assertEqual( l.vertical, False )
        self.assertEqual( l.a, -0.5 )
        self.assertEqual( l.b, 2 )

        l = line( point( 1, 2 ), point( 2, 1 ) )
        self.assertEqual( l.vertical, False )
        self.assertEqual( l.a, -1 )
        self.assertEqual( l.b, 3 )

        l = line( point( 10, 2 ), point( 10, 10 ) )
        self.assertEqual( l.vertical, True )
        self.assertEqual( l.x, 10 )

    def test_invalid_line(self):
        with self.assertRaises( AssertionError ):
            line( point( 0, 0 ), point( 0, 0 ) )


if __name__ == "__main__":
    unittest.main( )
