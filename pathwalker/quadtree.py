import unittest
from geometry import Point, LineSegment, BoundingBox, intersect_line_segment_and_bounding_box

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












def do_bounding_boxes_intersect_not_including_upper_limits( bounding_box, non_including_bounding_box ):
	"""Checks whether two bounding boxes intersect, taking into account that one the boxes has
	non-including upper limits."""
	intersection = non_including_bounding_box.intersect( bounding_box )

	if intersection is None:
		return False

	if ( intersection.x_lower == non_including_bounding_box.x_upper
		 or intersection.y_lower == non_including_bounding_box.y_upper ):
		return False

	return True


def do_line_segment_and_bounding_box_intersect_not_including_upper_limits( segment, non_including_bounding_box ):
	"""Checks whether linesegemnt and bounding box intersect, taking into account that upper limits of
	the bounding box are non-including."""

	intersection = intersect_line_segment_and_bounding_box( segment, non_including_bounding_box )

	if intersection is None:
		return False

	intersection_bounding_box = intersection.get_bounding_box()
	if ( intersection_bounding_box.x_lower == non_including_bounding_box.x_upper
		 or intersection_bounding_box.y_lower == non_including_bounding_box.y_upper ):
		return False

	return True


def is_bounding_box_fully_inside_bounding_box_not_including_upper_limits( bounding_box, non_including_bounding_box ):
	"""Checks whether a bounding box is fully inside another bounding box, for which upper limits are not included."""
	intersection = bounding_box.intersect( non_including_bounding_box )
	if intersection is None or intersection != bounding_box:
		return False

	if ( bounding_box.x_upper == non_including_bounding_box.x_upper
		 or bounding_box.y_upper == non_including_bounding_box.y_upper ):
		return False

	return True


def break_bounding_box_into_quadrants( bounding_box ):
	"""Return four bounding boxes representing four quadrants of a given bounding box."""
	x_middle = ( bounding_box.x_lower + bounding_box.x_upper ) / 2
	y_middle = ( bounding_box.y_lower + bounding_box.y_upper ) / 2
	return ( BoundingBox( bounding_box.x_lower, x_middle, bounding_box.y_lower, y_middle ),
			 BoundingBox( x_middle, bounding_box.x_upper, bounding_box.y_lower, y_middle ),
			 BoundingBox( bounding_box.x_lower, x_middle, y_middle, bounding_box.y_upper ),
			 BoundingBox( x_middle, bounding_box.x_upper, y_middle, bounding_box.y_upper ) )


class QuadTree:
	"""Quad tree for lines."""

	class QuadTreeQuadrant:
		def __init__(self, bounding_box, max_elems, level, max_level):
			self.bounding_box = bounding_box
			self.elems = []
			self.max_elems = max_elems
			self.level = level
			self.max_level = max_level
			self.subquadrants = None

		def add(self, line):
			if not do_line_segment_and_bounding_box_intersect_not_including_upper_limits( line, self.bounding_box ):
				return

			if len( self.elems ) >= self.max_elems and self.level < self.max_level:
				self.subquadrants = tuple(
					QuadTree.QuadTreeQuadrant( quadrant_bounding_box, self.max_elems, self.level + 1, self.max_level )
					for quadrant_bounding_box in break_bounding_box_into_quadrants( self.bounding_box )
				)
				for quadrant in self.subquadrants:
					for elem in self.elems:
						quadrant.add( elem )
				self.elems = []

			if self.subquadrants is not None:
				for subquadrant in self.subquadrants:
					subquadrant.add( line )
			else:
				self.elems.append( line )

		def get(self, bounding_box):
			if not do_bounding_boxes_intersect_not_including_upper_limits( bounding_box, self.bounding_box ):
				return []

			if self.subquadrants is not None:
				result = []
				for subquadrant in self.subquadrants:
					result += subquadrant.get( bounding_box )
				return result
			else:
				return self.elems

	def __init__( self, x1, x2, y1, y2, max_elems = 8, max_level = 8 ):
		self.main_bounding_box = BoundingBox( x1, x2, y1, y2 )
		self.max_elems = max_elems
		self.max_level = max_level

		self.elems_around_root_quadrant = []
		self.main_quadrant = QuadTree.QuadTreeQuadrant( self.main_bounding_box, self.max_elems, 0, self.max_level )

	def add( self, line ):
		self.main_quadrant.add( line )
		if ( not is_bounding_box_fully_inside_bounding_box_not_including_upper_limits( line.get_bounding_box(),
																					   self.main_bounding_box ) ):
			self.elems_around_root_quadrant.append( line )

	def get( self, bounding_box ):
		if ( not is_bounding_box_fully_inside_bounding_box_not_including_upper_limits( bounding_box,
																					   self.main_bounding_box ) ):
			return self.main_quadrant.get( bounding_box ) + self.elems_around_root_quadrant

		return self.main_quadrant.get( bounding_box )


class QuadTreeTests(unittest.TestCase):
	def test_quad_tree(self):
		quad_tree = QuadTree( 0, 0, 100, 100 )
		quad_tree.add( LineSegment( Point( 10, 10 ), Point( 20, 20 ) ) )
		quad_tree.get( BoundingBox( 10, 90, 10, 90 ) )

	def test_non_including_bounding_boxes_intersection(self):
		self.assertTrue( do_bounding_boxes_intersect_not_including_upper_limits( BoundingBox( 1, 2, 1, 2 ),
																				 BoundingBox(0, 10, 0, 10) ) )
		self.assertFalse( do_bounding_boxes_intersect_not_including_upper_limits( BoundingBox( 10, 11, 1, 2 ),
																				  BoundingBox(0, 10, 0, 10) ) )
		self.assertFalse( do_bounding_boxes_intersect_not_including_upper_limits( BoundingBox( 1, 2, 10, 12 ),
																				  BoundingBox( 0, 10, 0, 10 ) ) )
		self.assertFalse( do_bounding_boxes_intersect_not_including_upper_limits( BoundingBox( 10, 12, 10, 12 ),
																				  BoundingBox( 0, 10, 0, 10 ) ) )

	def test_line_segment_and_non_including_bounding_box_intersection(self):
		self.assertTrue( do_line_segment_and_bounding_box_intersect_not_including_upper_limits(
			LineSegment( Point( 1, 1 ), Point( 2, 2 ) ),
			BoundingBox(0, 10, 0, 10) ) )
		self.assertTrue( do_line_segment_and_bounding_box_intersect_not_including_upper_limits(
			LineSegment( Point( -1, 1 ), Point( 1, -1 ) ),
			BoundingBox(0, 10, 0, 10) ) )

		self.assertFalse( do_line_segment_and_bounding_box_intersect_not_including_upper_limits(
			LineSegment( Point( -1, 1 ), Point( 0.99, -1 ) ),
			BoundingBox(0, 10, 0, 10) ) )
		self.assertFalse( do_line_segment_and_bounding_box_intersect_not_including_upper_limits(
			LineSegment( Point( 10, 1 ), Point( 10, -1 ) ),
			BoundingBox(0, 10, 0, 10) ) )
		self.assertFalse( do_line_segment_and_bounding_box_intersect_not_including_upper_limits(
			LineSegment( Point( 1, 10 ), Point( 2, 10 ) ),
			BoundingBox(0, 10, 0, 10) ) )

	def test_is_bounding_box_fully_inside_bounding_box_not_including_upper_limits(self):
		self.assertTrue( is_bounding_box_fully_inside_bounding_box_not_including_upper_limits(
			BoundingBox( 1, 2, 1, 2 ), BoundingBox( 0, 10, 0, 10 ) ) )
		self.assertTrue( is_bounding_box_fully_inside_bounding_box_not_including_upper_limits(
			BoundingBox( 0, 2, 0, 2 ), BoundingBox( 0, 10, 0, 10 ) ) )

		self.assertFalse( is_bounding_box_fully_inside_bounding_box_not_including_upper_limits(
			BoundingBox( -0.01, 2, 0, 2 ), BoundingBox( 0, 10, 0, 10 ) ) )
		self.assertFalse( is_bounding_box_fully_inside_bounding_box_not_including_upper_limits(
			BoundingBox(20, 21, 20, 21 ), BoundingBox( 0, 10, 0, 10 ) ) )
		self.assertFalse( is_bounding_box_fully_inside_bounding_box_not_including_upper_limits(
			BoundingBox(9, 10, 0, 1 ), BoundingBox( 0, 10, 0, 10 ) ) )
		self.assertFalse( is_bounding_box_fully_inside_bounding_box_not_including_upper_limits(
			BoundingBox(5, 6, 9, 10 ), BoundingBox( 0, 10, 0, 10 ) ) )






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

		#self.assertFalse(NonIncludingBoundingBox(0, 10, 0, 10).does_intersect_line(
		#	LineSegment(Point(0, -10), Point(10, 0))))

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