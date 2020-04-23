import unittest
from geometry import Point, LineSegment, BoundingBox

def check_inside_bounds( value, lower, upper, upper_included = True):
	if upper_included:
		return lower <= value and value <= upper
	else:
		return lower <= value and value < upper

def check_bounds_intersect( first_lower, first_upper, second_lower, second_upper, second_upper_included = True ):
	assert( first_lower <= first_upper and second_lower <= second_upper )
	if ( check_inside_bounds( first_lower, second_lower, second_upper, second_upper_included )
         or check_inside_bounds( first_upper, second_lower, second_upper, second_upper_included ) ):
		return True

	if check_inside_bounds( second_lower, first_lower, first_upper ):
		return True

	if second_upper_included:
		return check_inside_bounds( second_upper, first_lower, first_upper )
	else:
		return first_lower < second_upper and second_upper <= first_upper

class NonIncludingBoundingBox:
	"""Bounding box class. NOTE! Lower limits are considered included, upper - are not."""
	def __init__( self, x1, x2, y1, y2 ):
		assert( x1 != x2 and y1 != y2 )
		self.x_lower, self.x_upper = sorted( ( x1, x2 ) )
		self.y_lower, self.y_upper = sorted( ( y1, y2 ) )

	def does_intersect_line( self, segment ):
		"""Checks whether any point of the line is inside this bounding box.
		Type of line is assumed geometry.LineSegment."""
		if segment.vertical:
			return ( self.x_lower <= segment.x and segment.x < self.x_upper
				     and check_bounds_intersect( segment.start.y, segment.end.y, self.y_lower, self.y_upper, False ) )

		x_intersect_lower = max( self.x_lower, segment.start.x )
		if segment.end.x < self.x_upper:
			x_intersect_upper = segment.end.x

			if x_intersect_lower > x_intersect_upper:
				return False

			y_intersect_lower = segment.point_at_x( x_intersect_lower ).y
			y_intersect_upper = segment.point_at_x( x_intersect_upper ).y

			y_intersect_lower, y_intersect_upper = sorted( ( y_intersect_lower, y_intersect_upper ) )

			return check_bounds_intersect( y_intersect_lower, y_intersect_upper, self.y_lower, self.y_upper, False )
		else:
			x_intersect_upper = self.x_upper

			if x_intersect_lower >= x_intersect_upper:
				return False

			y_intersect_lower = segment.point_at_x( x_intersect_lower ).y
			y_intersect_upper = segment.point_at_x( x_intersect_upper ).y

			y_intersect_lower, y_intersect_upper = sorted( ( y_intersect_lower, y_intersect_upper ) )

			return check_bounds_intersect( y_intersect_lower, y_intersect_upper, self.y_lower, self.y_upper, False )


	def does_intersect_other_bounding_box( self, bounding_box ):
		"""Checks whether bounding_box has any common point with this bounding box.
		NOTE!!! For this bound box upper limits are considered not included, for bounding_box - they are
		considered included. bounding_box type is expected to be geometry.BoundingBox."""
		return ( check_bounds_intersect( bounding_box.x_lower, bounding_box.x_upper, self.x_lower, self.x_upper, False )
		 		 and check_bounds_intersect( bounding_box.y_lower, bounding_box.y_upper, self.y_lower, self.y_upper, False ) )


class QuadTree:
	"""Quad tree for lines."""

	def __init__( self, x1, x2, y1, y2, max_elems, level, max_level ):
		self.x_start, self.x_end = sorted( x1, x2 )
		self.y_start, self.y_end = sorted( y1, y2 )

		self.elems = []
		self.max_elems = max_elems

		self.level = level
		self.max_level = max_level

	def add( self, line ):
		pass

	def get_all( self, bounding_box ):
		pass


class QuadTreeTests(unittest.TestCase):
	def test_bounds_intersection(self):
		self.assertTrue( check_bounds_intersect( 10, 20, 10, 20 ) )
		self.assertTrue( check_bounds_intersect( 10, 20, 5, 15 ) )
		self.assertTrue( check_bounds_intersect( 10, 20, 15, 25 ) )
		self.assertTrue( check_bounds_intersect( 10, 20, 5, 25 ) )

		self.assertTrue( check_bounds_intersect( 10, 20, 20, 30 ) )

		self.assertTrue( check_bounds_intersect( 5, 15, 10, 20 ) )
		self.assertTrue( check_bounds_intersect( 15, 25, 10, 20 ) )
		self.assertTrue( check_bounds_intersect( 5, 25, 10, 20 ) )

		self.assertFalse(check_bounds_intersect( 20, 30, 10, 19 ) )
		self.assertFalse(check_bounds_intersect( 20, 30, 31, 40 ) )

		self.assertFalse( check_bounds_intersect( 20, 30, 10, 20, False ) )

	def test_intersect_bounding_boxes( self ):
		self.assertTrue( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_other_bounding_box( BoundingBox( 1, 9, 1, 9 ) ) )
		self.assertTrue( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_other_bounding_box( BoundingBox( -11, 1, 1, 9 ) ) )
		self.assertFalse( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_other_bounding_box( BoundingBox( -11, -0.1, 1, 9 ) ) )

		self.assertTrue( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_other_bounding_box( BoundingBox( 9, 20, 1, 9 ) ) )
		self.assertFalse( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_other_bounding_box( BoundingBox( 10, 20, 1, 9 ) ) )
		self.assertFalse( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_other_bounding_box( BoundingBox( 11, 20, 1, 9 ) ) )

		self.assertTrue( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_other_bounding_box( BoundingBox( -10, 0, -10, 0 ) ) )
		self.assertFalse( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_other_bounding_box( BoundingBox( 10, 10, 20, 20 ) ) )

	def test_intersect_vertical_line( self ):
		self.assertTrue( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_line(
			LineSegment( Point( 1, -1 ), Point( 1, 11 ) ) ) )
		self.assertTrue( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_line(
			LineSegment( Point( 1, 1 ), Point( 1, 11 ) ) ) )
		self.assertTrue( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_line(
			LineSegment( Point( 1, -1 ), Point( 1, 1 ) ) ) )
		self.assertTrue( NonIncludingBoundingBox( 0, 10, 0, 10 ).does_intersect_line(
			LineSegment( Point( 1, 1 ), Point( 1, 2 ) ) ) )

		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(-1, 1), Point(-1, 2))))
		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(20, 1), Point(20, 2))))

		self.assertTrue(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(0, 1), Point(0, 2))))
		self.assertTrue(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(5, 0), Point(5, -20))))

		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(5, 10), Point(5, 20))))
		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(10, 1), Point(10, 2))))

	def test_intersect_line( self ):
		self.assertTrue(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(0, 0), Point(10, 10))))
		self.assertTrue(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(0, 0), Point(10, -10))))
		self.assertTrue(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(9, 0), Point(10, -10))))
		self.assertTrue(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(0, 1), Point(-10, -10))))
		self.assertTrue(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(1, 0), Point(-10, -10))))

		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(0, -10), Point(10, 0))))

		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(11, 9), Point(20, 0))))
		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(10, 9), Point(20, 0))))
		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(1, 10), Point(0, 20))))
		self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
			LineSegment(Point(0, 10), Point(100, 10))))

if __name__ == "__main__":
	unittest.main( )