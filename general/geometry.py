import unittest
import math

DEFAULT_PRECISION = 0.0000000001


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


def check_value_inside_bounds( value, bound1, bound2 ):
    if bound1 > bound2:
        bound1, bound2 = bound2, bound1
    return bound1 <= value and value <= bound2


class BoundingBox:
    """Bounding box class. All limits are considered included."""
    def __init__(self, x1, x2, y1, y2 ):
        self.x_lower, self.x_upper = sorted( ( x1, x2 ) )
        self.y_lower, self.y_upper = sorted( ( y1, y2 ) )

    def intersect(self, other):
        x_lower = max( self.x_lower, other.x_lower )
        x_upper = min( self.x_upper, other.x_upper )

        if x_lower > x_upper:
            return None

        y_lower = max( self.y_lower, other.y_lower )
        y_upper = min( self.y_upper, other.y_upper )

        if y_lower > y_upper:
            return None

        return BoundingBox( x_lower, x_upper, y_lower, y_upper )

    def union(self, other):
        return BoundingBox( min( self.x_lower, other.x_lower ), max( self.x_upper, other.x_upper ),
                            min( self.y_lower, other.y_lower ), max( self.y_upper, other.y_upper ) )

    def expand( self, amount ):
        return BoundingBox( self.x_lower - amount, self.x_upper + amount, self.y_lower - amount, self.y_upper + amount )

    def __contains__(self, point):
        return ( self.x_lower <= point.x and point.x <= self.x_upper
                 and self.y_lower <= point.y and point.y <= self.y_upper )

    def __eq__( self, other ):
        return ( self.x_lower == other.x_lower
                 and self.x_upper == other.x_upper
                 and self.y_lower == other.y_lower
                 and self.y_upper == other.y_upper )

    def __ne__( self, other ):
        return not self.__eq__( other )

    def __str__(self):
        return "BoundingBox( x_lower={}, x_upper={}, y_lower={}, y_upper={} )".format( self.x_lower, self.x_upper,
                                                                                       self.y_lower, self.y_upper )

    def __repr__(self):
        return self.__str__( )


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def int_tuple(self):
        return int( self.x ), int( self.y )

    def equal_with_precision(self, other, precision = DEFAULT_PRECISION):
        return abs( self.x - other.x ) < precision and abs( self.y - other.y ) < precision

    def get_bounding_box(self):
        return BoundingBox( self.x, self.x, self.y, self.y )

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
        assert( type( p1 ) is Point )
        assert( type( p2 ) is Point )
        assert( p1 != p2 )

        if p1.x == p2.x:
            self.vertical = True
            self.x = p1.x
        else:
            self.vertical = False
            self.a = ( p1.y - p2.y ) / ( p1.x - p2.x )
            self.b = p1.y - p1.x * self.a

    def perpendicular(self, point):
        """Returns new line object, which is perpendicular to this one and goes through point."""
        perpendicular = Line(Point(0, 0), Point(0, 1))
        if self.vertical:
            perpendicular.vertical = False
            perpendicular.a = 0
            perpendicular.b = point.y
        elif self.a == 0:
            perpendicular.x = point.x
        else:
            perpendicular.vertical = False
            perpendicular.a = -1 / self.a
            perpendicular.b = point.y - perpendicular.a * point.x

        return perpendicular

    def point_at_x(self, x):
        assert( not self.vertical )
        return Point( x, self.a * x + self.b )

    def mirror(self, point):
        """Returns new Point object which is reflected (mirrored) against this line."""
        projection = intersect_lines( self, self.perpendicular( point ) )
        return Point( 2 * projection.x - point.x, 2 * projection.y - point.y )

    def are_on_the_same_side(self, point1, point2):
        """Returns True if both point1 and point2 are on the same side in regard on this line."""
        if point1 in self or point2 in self:
            raise ValueError( "Point must not be on the line." )

        if self.vertical:
            return ( point1.x < self.x and point2.x < self.x
                     or point1.x > self.x and point2.x > self.x )

        projection1 = self.point_at_x( point1.x )
        projection2 = self.point_at_x( point2.x )

        return ( point1.y < projection1.y and point2.y < projection2.y
                 or point1.y > projection1.y and point2.y > projection2.y )

    def __contains__(self, point):
        assert( type( point ) is Point )

        if self.vertical:
            return point.x == self.x

        return point.x * self.a + self.b == point.y

    def __str__(self):
        if self.vertical:
            return "Line( vertical, x={} )".format( self.x )

        return "Line( a={}, b={} )".format( self.a, self.b )

    def __repr__(self):
        return self.__str__( );

    def __eq__(self, other):
        if type( other ) is not Line and not issubclass( type( other ), Line ):
            return False

        if self.vertical != other.vertical:
            return False

        if self.vertical:
            return self.x == other.x
        else:
            return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self == other


class LineSegment( Line ):
    def __init__(self, start, end ):
        Line.__init__( self, start, end )
        self.start = start
        self.end = end
        if self.vertical:
            if self.start.y > self.end.y:
                self.start, self.end = self.end, self.start
        else:
            if self.start.x > self.end.x:
                self.start, self.end = self.end, self.start

    def get_bounding_box(self):
        return BoundingBox( self.start.x, self.end.x, self.start.y, self.end.y )

    def intersect_bounding_box(self, bounding_box):
        return intersect_line_segment_and_bounding_box( self, bounding_box )

    def __str__(self):
        return "LineSegment( line={} start={} end={} )".format( Line.__str__( self ), self.start, self.end )

    def __repr__(self):
        return self.__str__( );

    def __contains__(self, point):
        assert( type( point ) is Point )
        if not Line.__contains__( self, point ):
            return False

        if self.vertical:
            return check_value_inside_bounds( point.y, self.start.y, self.end.y )

        return check_value_inside_bounds(point.x, self.start.x, self.end.x)

    def __eq__(self, other):
        if type( other ) is not LineSegment:
            return False

        return Line.__eq__( self, other ) and self.start == other.start and self.end == other.end


class Circle:
    def __init__( self, center, radius ):
        assert( radius > 0 )
        self.center = center
        self.radius = radius

    def get_bounding_box(self):
        return BoundingBox( self.center.x - self.radius, self.center.x + self.radius,
                            self.center.y - self.radius, self.center.y + self.radius )

    def __eq__(self, other):
        return type( other ) is Circle and self.center == other.center and self.radius == other.radius

    def __ne__(self, other):
        return not self == other


def distance( point1, point2 ):
    assert( type( point1 ) is Point )
    assert( type( point2 ) is Point )

    from math import sqrt

    return sqrt( ( point2.x - point1.x ) ** 2 + ( point2.y - point1.y ) ** 2 )


def intersect_lines( line1, line2 ):
    """Calculates point of intersection of two lines.
    If lines do not intersect - returns None.
    If line do intersect - returns point object with value of point of intersection.
    If lines are the same - meaning there are infinite number of points of intersection - returns float( "Infinity" ).
    """

    if Line.__eq__( line1, line2 ):
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

def intersect_line_and_line_segment( line, line_segment ):
    """Calculates intersection of line and line segment.
    If they do not intersect - returns None.
    If they do intersect - returns Point object with value of point of intersection.
    If segment is contained by the line - it returns the line segment object."""

    lines_intersection = intersect_lines( line, line_segment )

    if lines_intersection is None:
        return None

    if lines_intersection == float( "Infinity" ):
        return line_segment

    if type( lines_intersection ) is Point:
        is_intersection_on_line_segment = ( check_value_inside_bounds(lines_intersection.y, line_segment.start.y, line_segment.end.y)
                                            if line_segment.vertical
                                            else check_value_inside_bounds( lines_intersection.x, line_segment.start.x, line_segment.end.x) )
        if is_intersection_on_line_segment:
            return lines_intersection

    return None


def intersect_line_segments( segment1, segment2 ):
    """Calculates intersection of line and line segment.
    If they do not intersect - returns None.
    If they do intersect - returns Point object with value of point of intersection.
    If segment is contained by the line - it returns the line segment object."""

    # check bounding box intersection
    if segment1.get_bounding_box().intersect( segment2.get_bounding_box() ) is None:
        return None

    intersection = intersect_line_and_line_segment( segment1, segment2 )

    if intersection is None:
        return None

    if type( intersection ) is Point: # and intersection in segment1:
        is_intersection_on_segment1 = ( check_value_inside_bounds( intersection.y, segment1.start.y, segment1.end.y )
                                        if segment1.vertical
                                        else check_value_inside_bounds( intersection.x, segment1.start.x, segment1.end.x ) )
        if is_intersection_on_segment1:
            return intersection

    if type( intersection ) is LineSegment:
        # THIS IS TO BE CHANGED
        return 1

    return None

def intersect_line_and_circle( circle, line ):
    from math import sqrt

    def equidistant_points_on_line( line, point, dist ):
        if line.vertical:
            return ( Point( line.x, point.y + dist ), Point( line.x, point.y - dist ) )

        x_span = dist / sqrt( 1 + line.a ** 2 )

        return ( Point( point.x + x_span, line.a * (point.x + x_span ) + line.b ),
                 Point( point.x - x_span, line.a * (point.x - x_span ) + line.b ) )

    if circle.center in line:
        # line goes through circle.center
        return equidistant_points_on_line( line, circle.center, circle.radius )

    # more general case: create perpendicular to line that goes through circle.center
    perpendicular =  line.perpendicular( circle.center )
    closest_point = intersect_lines( line, perpendicular )
    distance_to_closest_point = distance( closest_point, circle.center )

    if distance_to_closest_point > circle.radius:
        return tuple( )
    elif distance_to_closest_point == circle.radius:
        return ( closest_point, )
    else:
        span = sqrt( circle.radius ** 2 - distance_to_closest_point ** 2 )
        return equidistant_points_on_line( line, closest_point, span )


def intersect_line_segment_and_circle( circle, segment ):
    """Returns iterable of Points where line segment and circle intersects.
    Points are sorted by their distance to segment.start - meaning the closest will be first."""

    # check whether their bounding boxes even intersect
    if circle.get_bounding_box().intersect( segment.get_bounding_box() ) is None:
        return tuple( )

    line_circle_intersection = intersect_line_and_circle( circle, segment )

    if segment.vertical:
        def check_point_belongs_to_segment( point ):
            return check_value_inside_bounds( point.y, segment.start.y, segment.end.y )
    else:
        def check_point_belongs_to_segment( point ):
            return check_value_inside_bounds( point.x, segment.start.x, segment.end.x )

    return tuple( filter( check_point_belongs_to_segment, line_circle_intersection ) )


def measure_out( start, end, distance ):
    """Returns a point, which lies at distance from start in the direction of end."""
    assert( start != end )

    if start.x == end.x:
        direction = 1 if start.y < end.y else -1
        return Point( start.x, start.y + direction * distance )

    direction = 1 if start.x < end.x else -1
    movement_line = Line( start, end )
    x_change = distance / math.sqrt( movement_line.a ** 2 + 1 )

    return movement_line.point_at_x( start.x + direction * x_change )


def intersect_bounds( a_lower, a_upper, b_lower, b_upper ):
    if a_lower > a_upper:
        a_lower, a_upper = a_upper, a_lower
    if b_lower > b_upper:
        b_lower, b_upper = b_upper, b_lower

    lower = max( a_lower, b_lower )
    upper = min( a_upper, b_upper )

    if lower > upper:
        return None

    return lower, upper


def intersect_line_segment_and_bounding_box( segment, bounding_box ):
    segment_bounding_box = segment.get_bounding_box()
    bounding_boxes_intersection = bounding_box.intersect( segment_bounding_box )

    if bounding_boxes_intersection is None:
        return None

    if bounding_boxes_intersection == segment_bounding_box:
        return segment

    if segment.vertical:
        if bounding_boxes_intersection.y_lower == bounding_boxes_intersection.y_upper:
            return Point( segment.x, bounding_boxes_intersection.y_lower )

        return LineSegment( Point( segment.x, bounding_boxes_intersection.y_lower ),
                            Point( segment.x, bounding_boxes_intersection.y_upper ) )

    if segment.start.y == segment.end.y:
        # horizontal line
        if not ( bounding_box.y_lower <= segment.start.y and segment.start.y <= bounding_box.y_upper ):
            return None

        if bounding_boxes_intersection.x_lower == bounding_boxes_intersection.x_upper:
            return Point( bounding_boxes_intersection.x_lower, segment.start.y )

        return LineSegment( Point( bounding_boxes_intersection.x_lower, segment.start.y ),
                            Point( bounding_boxes_intersection.x_upper, segment.start.y ) )

    ys_intersection = intersect_bounds( bounding_box.y_lower, bounding_box.y_upper,
                                        segment.point_at_x( bounding_boxes_intersection.x_lower ).y,
                                        segment.point_at_x( bounding_boxes_intersection.x_upper ).y )

    if ys_intersection is None:
        return None

    if ys_intersection[0] == ys_intersection[1]:
        return Point( ( ys_intersection[0] - segment.b ) / segment.a, ys_intersection[0] )

    return LineSegment( Point( ( ys_intersection[0] - segment.b ) / segment.a, ys_intersection[0] ),
                        Point( ( ys_intersection[1] - segment.b ) / segment.a, ys_intersection[1] ) )


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
        self.assertTrue( Point( 0, 0 ) in Line( Point( 0, 0 ), Point( 0, 10 ) ) )
        self.assertFalse( Point( 0.1, 0 ) in Line( Point( 0, 0 ), Point( 0, 10 ) ) )
        self.assertTrue( Point( 1, 1 ) in Line( Point( 0, 0 ), Point( 10, 10 ) ) )
        self.assertFalse( Point( 1, 2 ) in Line( Point( 0, 0 ), Point( 10, 10 ) ) )

    def test_point_at_x( self ):
        self.assertEqual( Line( Point( 0, 0 ), Point( 1, 0 ) ).point_at_x( 10 ),
                          Point( 10, 0 ) )
        self.assertEqual( Line( Point( 0, 0 ), Point( 2, 1 ) ).point_at_x( 10 ),
                          Point( 10, 5 ) )
        with self.assertRaises( AssertionError ):
            Line(Point(0, 0), Point(0, 1)).point_at_x(10)

    def test_is_point_on_line_segment( self ):
        self.assertFalse( Point( 0, -1 ) in LineSegment( Point( 0, 0 ), Point( 0, 10 ) ) )
        self.assertTrue( Point( 0, 0 ) in LineSegment( Point( 0, 0 ), Point( 0, 10 ) ) )
        self.assertTrue( Point( 0, 5 ) in LineSegment( Point( 0, 0 ), Point( 0, 10 ) ) )
        self.assertTrue( Point( 0, 10 ) in LineSegment( Point( 0, 0 ), Point( 0, 10 ) ) )
        self.assertFalse( Point( 0, 10.001 ) in LineSegment( Point( 0, 0 ), Point( 0, 10 ) ) )

        self.assertFalse( Point( 0.1, 0 ) in LineSegment( Point( 0, 0 ), Point( 0, 10 ) ) )

        self.assertFalse( Point( -1, -1 ) in LineSegment( Point( 0, 0 ), Point( 10, 10 ) ) )
        self.assertTrue( Point( 1, 1 ) in LineSegment( Point( 0, 0 ), Point( 10, 10 ) ) )
        self.assertFalse( Point( 11, 11 ) in LineSegment( Point( 0, 0 ), Point( 10, 10 ) ) )
        self.assertFalse( Point( 1, 2 ) in LineSegment( Point( 0, 0 ), Point( 10, 10 ) ) )

    def test_distance( self ):
        self.assertEqual( distance( Point( 0, 0 ), Point( 10, 0 ) ), 10 )
        self.assertEqual( distance( Point( 0, 10 ), Point( 10, 10 ) ), 10 )
        self.assertEqual( distance( Point( 0, 10 ), Point( 100, 11 ) ), 100.00499987500625 )

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

        self.assertEqual( intersect_lines( Line( Point( 0, 10 ), Point( -2, 0 ) ),
                                           Line( Point( 1, 1 ), Point( -4, 2 ) ) ),
                          Point( -1.6923076923076923, 1.5384615384615383 ) )


    def test_intersect_line_and_circle( self ):
        # cases where line goes through circle's center
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

        # cases where line does not intersect circle
        self.assertEqual( intersect_line_and_circle( Circle( Point( 1, 1 ), 1 ),
                                                     Line( Point( 10, 0 ), Point( 10, 1 ) ) ),
                          tuple( ) )
        self.assertEqual( intersect_line_and_circle( Circle( Point( 1, 1 ), 1 ),
                                                     Line( Point( 10, 2.1 ), Point( -10, 2.1 ) ) ),
                          tuple( ) )
        self.assertEqual( intersect_line_and_circle( Circle( Point( 1, 1 ), 1 ),
                                                     Line( Point( 100, 2.1 ), Point( -10, -100 ) ) ),
                          tuple( ) )

        # cases where line intersects circle in one place
        self.assertEqual( intersect_line_and_circle( Circle( Point( 5, 5 ), 3 ),
                                                     Line( Point( 10, 2 ), Point( 1000, 2 ) ) ),
                          ( Point( 5, 2 ), ) )
        self.assertEqual( intersect_line_and_circle( Circle( Point( 5, 5 ), 3 ),
                                                     Line( Point( 8, 7 ), Point( 8, 2 ) ) ),
                          ( Point( 8, 5 ), ) )
        self.assertEqual( intersect_line_and_circle( Circle( Point( 5, 5 ), 5.020458146424487 ),
                                                     Line( Point( 0, 2.9 ), Point( 2.9, 0 ) ) ),
                          ( Point( 1.45, 1.45 ), ) )

        # cases where line intersects circle in two places
        self.assertEqual( intersect_line_and_circle( Circle( Point( 1, 1 ), 5 ),
                                                     Line( Point( -1, 1 ), Point( -1, 0 ) ) ),
                          ( Point( -1, 5.58257569495584 ), Point( -1, -3.58257569495584 ) ) )
        self.assertEqual( intersect_line_and_circle( Circle( Point( 1, 1 ), 5 ),
                                                     Line( Point( 0, 4 ), Point( -2, 4 ) ) ),
                          ( Point( 5, 4 ), Point( -3, 4 ) ) )

        self.assertEqual( intersect_line_and_circle( Circle( Point( 1, 1 ), 5 ),
                                                     Line( Point( 0, 10 ), Point( -2, 0 ) ) ),
                          ( Point( -0.872797086436057, 5.636014567819715 ),
                            Point( -2.5118182981793273, -2.5590914908966376 ) ) )

    def test_intersect_line_segment_and_circle(self):
        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 0, 0 ), 10 ),
                                                             LineSegment( Point( 0, 0 ), Point( 0, -1 ) ) ),
                          tuple( ) )
        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 0, 0 ), 10 ),
                                                             LineSegment( Point( 0, 0 ), Point( 0, -100 ) ) ),
                          ( Point( 0, -10 ), ) )
        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 0, 0 ), 10 ),
                                                             LineSegment( Point( 0, 10 ), Point( 0, -100 ) ) ),
                          ( Point( 0, 10 ), Point( 0, -10 ) ) )
        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 0, 0 ), 10 ),
                                                             LineSegment( Point( 0, -100 ), Point( 0, 10 ) ) ),
                          ( Point( 0, 10 ), Point( 0, -10 ) ) )

        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 1, 1 ), 5 ),
                                                             LineSegment( Point( 0, 10 ), Point( -4, -10 ) ) ),
                          ( Point( -0.872797086436057, 5.636014567819715 ),
                            Point( -2.5118182981793273, -2.5590914908966376 ) ) )

        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 1, 1 ), 5 ),
                                                             LineSegment( Point( -4, -10 ), Point( 0, 10 ) ) ),
                          ( Point( -0.872797086436057, 5.636014567819715 ),
                            Point( -2.5118182981793273, -2.5590914908966376 ) ) )

        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 1, 1 ), 5 ),
                                                             LineSegment( Point( 0, 10 ), Point( -2, 0 ) ) ),
                          ( Point( -0.872797086436057, 5.636014567819715 ), ) )
        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 1, 1 ), 5 ),
                                                             LineSegment( Point( -2, 0 ), Point( -4, -10 ) ) ),
                          ( Point( -2.5118182981793273, -2.5590914908966376 ), ) )
        self.assertEqual( intersect_line_segment_and_circle( Circle( Point( 1, 1 ), 5 ),
                                                             LineSegment( Point( -2, 0 ), Point( -1, 5 ) ) ),
                          tuple( ) )

    def test_perpendicular(self):
        self.assertEqual( Line( Point( 0, 0 ), Point( 0, 1 ) ).perpendicular( Point( 20, 20 ) ),
                          Line( Point( 1, 20 ), Point( 0, 20 ) ) )
        self.assertEqual( Line( Point( 0, 0 ), Point( 0, 1 ) ).perpendicular( Point( 20, 0 ) ),
                          Line( Point( 1, 0 ), Point( 0, 0 ) ) )

        self.assertEqual( Line( Point( 0, 0 ), Point( 200, 0 ) ).perpendicular( Point( 20, 20 ) ),
                          Line( Point( 20, 1 ), Point( 20, 0 ) ) )
        self.assertEqual( Line( Point( 0, 0 ), Point( 200, 0 ) ).perpendicular( Point( 10000, 20 ) ),
                          Line( Point( 10000, 1 ), Point( 10000, 0 ) ) )

        self.assertEqual( Line( Point( 2, 8 ), Point( -1, 0 ) ).perpendicular( Point( 0.5, 4 ) ),
                          Line( Point( 0.5, 4 ), Point( 4.5, 2.5 ) ) )

    def test_mirror(self):
        self.assertEqual(Line(Point(0, 0), Point(0, 1)).mirror(Point(20, 20)),
                         Point(-20, 20))
        self.assertEqual(Line(Point(0, 0), Point(2, 1)).mirror(Point(10, 10)),
                         Point(14, 2))
        self.assertEqual(Line(Point(1, 1), Point(3, 0)).mirror(Point(11, 11)),
                         Point(-1, -13))

    def test_intersect_line_and_line_segment(self):
        self.assertEqual( intersect_line_and_line_segment( Line( Point( 1, 1 ), Point( 10, 10 ) ),
                                                           LineSegment( Point( 0, 1 ), Point( -1, 0 ) ) ),
                          None )

        self.assertEqual( intersect_line_and_line_segment( Line( Point( 0, 0 ), Point( -1, 1 ) ),
                                                           LineSegment( Point( 0, 1 ), Point( -1, 0 ) ) ),
                          Point( -0.5, 0.5 ) )

        self.assertEqual( intersect_line_and_line_segment( Line( Point( -2, 2 ), Point( -1, 1 ) ),
                                                           LineSegment( Point( -2, -1 ), Point( -1, 0 ) ) ),
                          None )

        self.assertEqual( LineSegment( Point( -2, 0 ), Point( 0, 0 ) ),
                          intersect_line_and_line_segment( Line( Point( 0, 0 ), Point( 10, 0 ) ),
                                                           LineSegment( Point( -2, 0 ), Point( 0, 0 ) ) ) )

        self.assertEqual( intersect_line_and_line_segment( Line(Point(-1, 0), Point(1, 0) ),
                                                           LineSegment( Point( 0, -1 ), Point( 0, -10 ) ) ),
                          None )


    def test_intersect_line_segments(self):
        self.assertEqual( intersect_line_segments( LineSegment( Point( 1, 1 ), Point( 10, 10 ) ),
                                                   LineSegment( Point( 0, 1 ), Point( -1, 0 ) ) ),
                          None )
        self.assertEqual( intersect_line_segments( LineSegment( Point( 0, 0 ), Point( -1, 1 ) ),
                                                   LineSegment( Point( 0, 1 ), Point( -1, 0 ) ) ),
                          Point( -0.5, 0.5 ) )
        self.assertEqual( intersect_line_segments( LineSegment( Point( -2, -1 ), Point( -1, 0 ) ),
                                                   LineSegment( Point( -2, 2 ), Point( -1, 1 ) ) ),
                          None )
        self.assertEqual( intersect_line_segments( LineSegment( Point( 0, -1 ), Point( 0, -10 ) ),
                                                   LineSegment(Point(-1, 0), Point(1, 0)) ),
                          None )

    def test_measure_out(self):
        def compare_points_with_proximity( p1, p2, precision = 0.03 ):
            return abs( p1.x-p2.x ) < precision and abs( p1.y-p2.y ) < precision

        self.assertEqual( Point( 5, 0 ),
                          measure_out( Point( 0, 0 ), Point( 10, 0 ), 5 ) )
        self.assertTrue( compare_points_with_proximity( Point( 5, 0.5 ),
                                                        measure_out(Point(0, 0), Point(10, 1), 5) ) )
        self.assertEqual( measure_out( Point( 0, 0 ), Point( 0, 1 ), 5 ),
                          Point( 0, 5 ) )

    def test_are_on_the_same_side(self):
        with self.assertRaises( ValueError ):
            Line(Point(0, 0), Point(0, 1)).are_on_the_same_side( Point( 1, 1 ), Point( 0, 10 ) )

        self.assertTrue( Line(Point(0, 0), Point(0, 1)).are_on_the_same_side( Point( 1, 1 ), Point( 1, 10 ) ) )
        self.assertTrue(Line(Point(0, 0), Point(0, 1)).are_on_the_same_side(Point(-10, 1), Point(-0.1, 10)))
        self.assertFalse(Line(Point(0, 0), Point(0, 1)).are_on_the_same_side(Point(10, 1), Point(-0.1, 10)))

        self.assertTrue(Line(Point(0, 0), Point(1, 1)).are_on_the_same_side(Point(10, 11), Point(-0.1, 0)))
        self.assertFalse(Line(Point(0, 0), Point(1, -1)).are_on_the_same_side(Point(10, 0), Point(-0.1, 0)))

    def test_intersect_bounding_boxes(self):
        self.assertEqual( BoundingBox( 0, 10, 0, 10 ).intersect( BoundingBox( 1, 9, 1, 9 ) ),
                          BoundingBox( 1, 9, 1, 9 ) )
        self.assertEqual( BoundingBox( 0, 10, 0, 10 ).intersect( BoundingBox( 1, 11, 1, 9 ) ),
                          BoundingBox( 1, 10, 1, 9 ) )
        self.assertEqual( BoundingBox( 0, 10, 0, 10 ).intersect( BoundingBox( 10, 11, 1, 9 ) ),
                          BoundingBox( 10, 10, 1, 9 ) )
        self.assertEqual( BoundingBox( 0, 10, 0, 10 ).intersect( BoundingBox( 10.001, 11, 1, 9 ) ),
                          None )

    def test_intersect_line_segment_and_bounding_box(self):
        # vertical lines
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( -1, 0 ), Point( -1, 10 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 20, 0 ), Point( 20, 10 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )

        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 3, -10 ), Point( 3, -1 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 4, 11 ), Point( 4, 12 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )

        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 5, 0 ), Point( 5, -1 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          Point( 5, 0 ) )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 5, 10 ), Point( 5, 11 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          Point( 5, 10 ) )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 5, 0 ), Point( 5, 10 ) ),
                                                                   BoundingBox( 0, 10, 5, 5 ) ),
                          Point( 5, 5 ) )

        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 1, 0 ), Point( 1, 10 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 1, 0 ), Point( 1, 10 ) ) )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 1, -1 ), Point( 1, 11 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 1, 0 ), Point( 1, 10 ) ) )

        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 1, -1 ), Point( 1, 5 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 1, 0 ), Point( 1, 5 ) ) )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 1, 11 ), Point( 1, 5 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 1, 10 ), Point( 1, 5 ) ) )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 1, 11 ), Point( 1, 5 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 1, 10 ), Point( 1, 5 ) ) )

        # non-vertical lines
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( -1, 11 ), Point( -10, 5 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 11, 11 ), Point( 20, 5 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )

        # horizontal lines
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 5, -1 ), Point( 7, -1 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 5, 11 ), Point( 7, 11 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )

        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 10, 8 ), Point( 11, 8 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          Point( 10, 8 ) )

        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 7, 8 ), Point( 11, 8 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 7, 8 ), Point( 10, 8 ) ) )

        # non-horizontal lines
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 0, -2 ), Point( 1, -1 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 0, 100 ), Point( 1, 11 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          None )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 0, 20 ), Point( 20, 0 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          Point( 10, 10 ) )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 1, -5 ), Point( 5, 5 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 3, 0 ), Point( 5, 5 ) ) )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( -1, 8 ), Point( 11, 2 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 0, 7.5 ), Point( 10, 2.5 ) ) )
        self.assertEqual( intersect_line_segment_and_bounding_box( LineSegment( Point( 2, -2 ), Point( -1, 4 ) ),
                                                                   BoundingBox( 0, 10, 0, 10 ) ),
                          LineSegment( Point( 0, 2 ), Point( 1, 0 ) ) )



if __name__ == "__main__":
    unittest.main( )
