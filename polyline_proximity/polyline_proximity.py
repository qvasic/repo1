import unittest

def line_intersection( line1, line2 ):
    """Find where two lines intersect.
    Lines are specified by two coordinates each.
    Returns tuple with coordination of intersection point, or None if they do not intersect. Also it returns None, if
    lines are equal."""

    if line1 == line2:
        # lines are equal
        return None

    if line1[0][0] == line1[1][0]:
        if line2[0][0] == line2[1][0]:
            # both lines are vertical
            return None
        return line_intersection( line2, line1 )

    def calc_line_equasion_coefs( line ):
        a = (line[1][1] - line[0][1]) / (line[1][0] - line[0][0])
        return a, line[0][1] - a * line[0][0]

    # first line is definitelly not vertical
    a1, b1 = calc_line_equasion_coefs( line1 )

    if line2[0][0] == line2[1][0]:
        # second line is vertical
        return line2[0][0], line2[0][0] * a1 + b1
    else:
        a2, b2 = calc_line_equasion_coefs( line2 )
        if a1 == a2:
            # line are parallel and do not intersect
            return None
        else:
            x = ( b2 - b1 ) / ( a1 - a2 )
            return x, a1*x + b1

def calculate_angle( x, y ):
    """Сalculates angle between coordinates origin and point ( x, y ), in radians."""
    import math
    if x == 0:
        return math.pi / 2 if y > 0 else -math.pi / 2

    if y > 0:
        if x > 0:
            return math.atan( y / x )
        else:
            return math.pi + math.atan( y / x )
    else:
        if x > 0:
            return math.atan( y / x )
        else:
            return - math.pi + math.atan( y / x )

def get_where_line_segments_are_in_proximity( segment1, segment2, threshold ):
    """Finds where first line segment is close enough to second line segment.
    Segments are specified by their start/end coordinates in ortogonal coordinates system: tuple of two tuple, e.g.
    ( (1, 2), ( 10, 10 ) ).
    Threshold is specified by a number, for example 1.0.
    Returns percentage range, where first segment is close enough to second one, percents are given in regard of first
    segment, meaning if it is close enough from the beginning of the first segment - then first value will be 0%.
    For example, return values can be ( 0, 50 ); ( 14, 75 ); None, if segments are never close enough.
    """

class TestPolylineProximityRoutines( unittest.TestCase ):

    def test_line_intersection(self):
        self.assertEqual( line_intersection( ( ( 0, 0 ), ( 1, 1 ) ), ( ( 0, 0 ), ( 1, 1 ) ) ),
                          None )
        self.assertEqual( line_intersection( ( ( 0, 0 ), ( 0, 1 ) ),
                                             ( ( 10, 0 ), ( 10, 1 ) ) ),
                          None )

        self.assertEqual( line_intersection( ( ( 0, 0 ), ( 1, 1 ) ),
                                             ( ( 1, 0 ), ( 1, 1 ) ) ),
                          ( 1, 1 ) )
        self.assertEqual( line_intersection( ( ( 0, 0 ), ( 1, 1 ) ),
                                             ( ( 1, 1 ), ( 2, 0 ) ) ),
                          ( 1, 1 ) )
        self.assertEqual( line_intersection( ( ( 4, 6 ), ( -2, -3 ) ),
                                             ( ( 4, -1 ), ( 1, 5 ) ) ),
                          ( 2, 3 ) )

    def test_line_intersection(self):
        from math import pi
        self.assertEqual( calculate_angle( 1, 0 ), 0 )
        
        self.assertEqual( calculate_angle( 1, 1 ), pi / 4 )
        self.assertEqual( calculate_angle( 0, 1 ), pi / 2 )
        self.assertEqual( calculate_angle( -1, 1 ), 3 * pi / 4 )

        self.assertEqual(calculate_angle( 1, -1 ), -pi / 4)
        self.assertEqual(calculate_angle(0, -1), -pi / 2)
        self.assertEqual(calculate_angle(-1, -1), 3 * -pi / 4)

if __name__ == "__main__":
    print( "hell0, running tests" )
    unittest.main( )
