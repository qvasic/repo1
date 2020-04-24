import unittest
from geometry import Point, LineSegment, BoundingBox, intersect_line_segment_and_bounding_box, intersect_line_segments
from random import randint
import time
from itertools import chain


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

	def __init__( self, bounding_box, max_elems = 8, max_level = 8 ):
		self.main_bounding_box = bounding_box
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
		line_ids = set( )
		result = []
		if ( not is_bounding_box_fully_inside_bounding_box_not_including_upper_limits( bounding_box,
																					   self.main_bounding_box ) ):
			excessive_line_list = chain( self.main_quadrant.get( bounding_box ), self.elems_around_root_quadrant )
		else:
			excessive_line_list = self.main_quadrant.get( bounding_box )

		for line in excessive_line_list:
			if id( line ) not in line_ids:
				line_ids.add( id( line ) )
				result.append( line )

		return result


class QuadTreeTests(unittest.TestCase):
	def random_point(bounding_box):
		return Point(randint(bounding_box.x_lower, bounding_box.x_upper),
					 randint(bounding_box.y_lower, bounding_box.y_upper))

	def time_this( call, *args, **kwargs ):
		start_time = time.time( )
		result = call( *args, **kwargs )
		end_time = time.time( )
		return end_time - start_time, result


	def test_quad_tree_smoke_test(self):
		quad_tree = QuadTree( 0, 0, 100, 100 )
		quad_tree.add( LineSegment( Point( 10, 10 ), Point( 20, 20 ) ) )
		self.assertEqual( quad_tree.get( BoundingBox( 10, 90, 10, 90 ) ),
						  [ LineSegment( Point( 10, 10 ), Point( 20, 20 ) ) ] )

	def test_quad_tree_load_test(self):
		quad_tree = QuadTree( BoundingBox( 0, 100, 0, 100 ) )
		points_bounding_box = BoundingBox( -10, 110, -10, 110 )
		for i in range( 200 ):
			point1 = QuadTreeTests.random_point( points_bounding_box )
			point2 = QuadTreeTests.random_point( points_bounding_box )
			while point1 == point2:
				point2 = QuadTreeTests.random_point( points_bounding_box )
			quad_tree.add( LineSegment( point1, point2 ) )

		self.assertTrue( type( quad_tree.get( BoundingBox( 10, 90, 10, 90 ) ) ) is list )

	def test_quad_tree_performance(self):
		segment_count = 35
		segment_size_variation = 20
		test_area = BoundingBox(0, 100, 0, 100)

		segments = []

		for i in range(segment_count):
			point1 = QuadTreeTests.random_point( test_area )
			point2 = Point( point1.x + randint( -segment_size_variation, segment_size_variation ),
							point1.y + randint( -segment_size_variation, segment_size_variation ) )
			while point1 == point2 or point2 not in test_area:
				point2 = Point(point1.x + randint(-segment_size_variation, segment_size_variation),
							   point1.y + randint(-segment_size_variation, segment_size_variation))

			"""
			point2 = QuadTreeTests.random_point( test_area )
			while point1 == point2:
				point2 = QuadTreeTests.random_point( test_area )
			"""
			segments.append( LineSegment( point1, point2 ) )

		def calculate_all_intersections_full_iteration( segments ):
			intersections = set( )
			for i in range( len( segments ) ):
				for j in range( i+1, len( segments ) ):
					intersection = intersect_line_segments( segments[i], segments[j] )
					if type( intersection ) is Point:
						intersections.add( ( intersection.x, intersection.y ) )

			return intersections

		def build_quad_tree( segments ):
			quad_tree = QuadTree( test_area )
			for segment in segments:
				quad_tree.add( segment )
			return quad_tree

		def calculate_all_intersections_quad_tree( segments, quad_tree ):
			intersections = set( )
			for segment in segments:
				possible_intersectors = quad_tree.get( segment.get_bounding_box( ) )
				for possible_intersector in possible_intersectors:
					if possible_intersector is segment:
						continue
					intersection = intersect_line_segments( segment, possible_intersector )
					if type( intersection ) is Point:
						intersections.add( ( intersection.x, intersection.y ) )

			return intersections

		full_iteration_intersections_time, full_iteration_intersections = QuadTreeTests.time_this(
			calculate_all_intersections_full_iteration, segments )
		quad_tree_build_time, quad_tree = QuadTreeTests.time_this( build_quad_tree, segments )
		quad_tree_intersections_time, quad_tree_intersections = QuadTreeTests.time_this(
			calculate_all_intersections_quad_tree, segments, quad_tree )

		print( "full iteration intersections took {:.3} seconds".format( full_iteration_intersections_time ) )
		print( "quad tree built in {:.3} seconds".format( quad_tree_build_time ) )
		print( "quad tree intersections took {:.3} seconds".format( quad_tree_intersections_time ) )

		self.assertEqual( full_iteration_intersections, quad_tree_intersections )



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


if __name__ == "__main__":
	unittest.main( )