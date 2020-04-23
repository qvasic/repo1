import geometry
import unittest


def remove_equal( l, equal = lambda x, y: x == y ):
    i = 0
    while i < len( l ):
        for j in range( i + 1, len( l ) ):
            if equal( l[i], l[j] ):
                l.pop( i )
                break
        else:
            i += 1


def is_line_segment_inside_intersection( line_segment, intersection_point1, intersection_point2 ):
    """Determines whether a line is at least partially inside an intersection with other figure.
    Intersection is defined by two points - intersection of line of line segment (yeah, right) with a figure
    (be it circle, or triangle, or rectangle)."""

    if line_segment.vertical:
        return ( geometry.check_value_inside_bounds( line_segment.start.y, intersection_point1.y, intersection_point2.y )
                 or geometry.check_value_inside_bounds( line_segment.end.y, intersection_point1.y, intersection_point2.y )
                 or geometry.check_value_inside_bounds( intersection_point1.y, line_segment.start.y, line_segment.end.y )
                 or geometry.check_value_inside_bounds( intersection_point2.y, line_segment.start.y, line_segment.end.y ) )
    else:
        return ( geometry.check_value_inside_bounds( line_segment.start.x, intersection_point1.x, intersection_point2.x )
                 or geometry.check_value_inside_bounds( line_segment.end.x, intersection_point1.x, intersection_point2.x )
                 or geometry.check_value_inside_bounds( intersection_point1.x, line_segment.start.x, line_segment.end.x )
                 or geometry.check_value_inside_bounds( intersection_point2.x, line_segment.start.x, line_segment.end.x ) )


def does_line_segment_interfere_with_circle( line_segment, circle ):
    """Basically finds out whether line segment is at least partially inside a circle.
    If line segment only "touches" the cirlce - it does not interfere."""

    intersection_points = geometry.intersect_line_and_circle( circle, line_segment )

    if len( intersection_points ) < 2:
        return False

    return is_line_segment_inside_intersection( line_segment, intersection_points[0], intersection_points[1] )


def does_line_segment_interfere_with_rect( line_segment, rect_segments ):
    """Basically determines whether line segment is at least partially inside a rectangle.
    Rectangle is defined by its edges, its definition is assumed to be correct and is not checked.
    Actually this should work not only for rectangles, but for any figure with only bulging corners.
    Yet this is not tested right now."""

    intersection_points = []

    for rect_segment in rect_segments:
        intersection = geometry.intersect_line_and_line_segment( line_segment, rect_segment )
        if type( intersection ) is geometry.Point:
            intersection_points.append( intersection )

    remove_equal( intersection_points, lambda x, y: x.equal_with_precision( y ) )

    if len( intersection_points ) > 2:
        raise ValueError( "Rectangle is incorrect, rect_segments={}, line_segment={}, intersection_points={}".format(
            rect_segments, line_segment, intersection_points ) )

    if len( intersection_points ) < 2:
        return False

    return is_line_segment_inside_intersection( line_segment, intersection_points[0], intersection_points[1] )

class ObstacleBypassTest(unittest.TestCase):
    def test_line_segment_interference_with_rect(self):
        point1 = geometry.Point( 2, 1 )
        point2 = geometry.Point( 1, 3 )
        point3 = geometry.Point( 9, 7 )
        point4 = geometry.Point( 10, 5 )

        rect_segments = [
            geometry.LineSegment( point1, point2 ),
            geometry.LineSegment( point2, point3 ),
            geometry.LineSegment( point3, point4 ),
            geometry.LineSegment( point4, point1 )
        ]

        self.assertTrue( does_line_segment_interfere_with_rect( geometry.LineSegment( geometry.Point( 5, 0 ),
                                                                                      geometry.Point( 5, 10 ) ),
                                                                rect_segments ) )
        self.assertTrue( does_line_segment_interfere_with_rect( geometry.LineSegment( geometry.Point( 5, 4 ),
                                                                                      geometry.Point( 5, 10 ) ),
                                                                rect_segments ) )
        self.assertTrue( does_line_segment_interfere_with_rect( geometry.LineSegment( geometry.Point( 5, 4 ),
                                                                                      geometry.Point( 5, 3 ) ),
                                                                rect_segments ) )
        self.assertTrue( does_line_segment_interfere_with_rect( geometry.LineSegment( geometry.Point( 2, 2 ),
                                                                                      geometry.Point( 4, 3 ) ),
                                                                rect_segments ) )

        self.assertFalse( does_line_segment_interfere_with_rect( geometry.LineSegment( geometry.Point( 3, 10 ),
                                                                                       geometry.Point( 3, 20 ) ),
                                                                rect_segments ) )

    def test_line_segment_interference_with_cirlce(self):
        circle = geometry.Circle( geometry.Point( 0, 0 ), 10 )

        self.assertTrue( does_line_segment_interfere_with_circle( geometry.LineSegment( geometry.Point( -20, 4 ),
                                                                                        geometry.Point( 20, 1 ) ),
                                                                  circle ) )
        self.assertTrue( does_line_segment_interfere_with_circle( geometry.LineSegment( geometry.Point( -5, 4 ),
                                                                                        geometry.Point( 20, 1 ) ),
                                                                  circle ) )
        self.assertTrue( does_line_segment_interfere_with_circle( geometry.LineSegment( geometry.Point( -5, 4 ),
                                                                                        geometry.Point( 4, 1 ) ),
                                                                  circle ) )

        self.assertFalse( does_line_segment_interfere_with_circle( geometry.LineSegment( geometry.Point( -50, 11 ),
                                                                                         geometry.Point( 50, 11 ) ),
                                                                   circle ) )


def main():
    unittest.main()

if __name__ == "__main__":
    main()