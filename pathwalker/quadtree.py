import unittest

def check_inside_bounds( value, lower, upper, upper_included = True):
	if upper_included:
		return lower <= value and value <= upper
	else:
		return lower <= value and value < upper

def check_bounds_intersect( first_lower, first_upper, second_lower, second_upper, second_upper_included = True ):
	if ( check_inside_bounds( first_lower, second_lower, second_upper, second_upper_included )
         or check_inside_bounds( first_upper, second_lower, second_upper, second_upper_included ) ):
		return True

	if check_inside_bounds( second_lower, first_lower, first_upper ):
		return True

	if second_upper_included:
		return check_inside_bounds( second_upper, first_lower, first_upper )
	else:
		return first_lower < second_upper and second_upper <= first_upper

class BoundingBox:
	"""Bounding box class. Lower limits are considered included, upper - are not."""
	def __init__( self, x1, x2, y1, y2 ):
		self.x_lower, self.x_upper = sorted( ( x1, x2 ) )
		self.y_lower, self.y_upper = sorted( ( y1, y2 ) ) 

	def does_intersect( self, line ):
		"""Checks whether any point of the line is inside this bounding box. Type of line is assumed geometry.Line."""
		if line.vertical:
			return self.x_lower <= line.x and line.x < self.x_upper

	def does_intersect( self, bounding_box ):
		pass


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

		self.assertFalse( check_bounds_intersect( 20, 30, 10, 20, False ) )


if __name__ == "__main__":
	unittest.main( )