"""
DONE:
- put geometry and pathfinder in separate module in separate project to be used by other projects
- figure out inheritance and eq operators in geometry module
- generate vertices only outside of angles
- change creating walls into sequence of walls
- debug absent edges - new wall [Point( 58, 48 ), Point( 58, 418 ), Point( 460, 439 ), Point( 464, 387 ), Point( 102, 375 ), Point( 103, 318 ), Point( 726, 357 ), Point( 715, 461 ), Point( 526, 449 ), Point( 517, 479 ), Point( 30, 460 ), Point( 27, 18 ), Point( 106, 20 ), Point( 98, 264 ), Point( 722, 306 ), Point( 722, 306 )]
- creation of "closed" walls
- implement is_line_walkable for walkers with size
- change removing corner into breaking wall into two
- add ability to connect two walls into one, just like finishing a loop
- is there a bug in checking final circle position in is_walkable function?
- add bounding box check to intersect_line_segments
- implement QuadTree
- improve QuadTree random testing, fix a bug there
- utilize QuadTree for pathwalker

TODO:
- intersection of line segments which are on the same line
- if destination if too close to a wall - move destination out
- corner cases for vertices generation - "not corner" corner, 0-degrees angle corner
- keep an eye for does_line_segment_interfere_with_rect exceptions
- refactor walls editing ui part, move appart walls editing, graph building, pathfinding and walking algos
- keep an eye on some rare flaky test failures for QuadTree
- REFACTOR THE SHT OUT OF ALL OF THAT

"""


import pygame
import math
import time
import json
import geometry
import pathfinder
from obstacle_bypass import does_line_segment_interfere_with_rect, does_line_segment_interfere_with_circle
from quadtree import QuadTree, get_line_segment_bounding_boxes

LEFT_MOUSE_BUTTON = 1
RIGHT_MOUSE_BUTTON = 3

def pixelate(surface, pixel_size = 2):
    origin_size = surface.get_size()
    rescale_size = (origin_size[0] // pixel_size, origin_size[1] // pixel_size)
    rescale_surface = pygame.transform.smoothscale(surface, rescale_size)
    pygame.transform.scale(rescale_surface, origin_size, surface)


def distance( p1, p2 ):
    return math.sqrt( ( p1[0]-p2[0] ) ** 2 + ( p1[1]-p2[1] ) ** 2 )


def check_hit( pos, hit, hit_size ):
    if (pos[0] - hit_size <= hit[0] and hit[0] <= pos[0] + hit_size
        and pos[1] - hit_size <= hit[1] and hit[1] <= pos[1] + hit_size):
        if distance(pos, hit) <= hit_size:
            return True

    return False


def pairwise( iterable ):
    iterator = iter( iterable )
    try:
        prev = next( iterator )
    except StopIteration:
        return

    for curr in iterator:
        yield prev, curr
        prev = curr


def vertices_for_line_segment_end( end, other_end, offset ):
    offset_center = geometry.measure_out( end, other_end, -offset )
    vertices = geometry.intersect_line_and_circle( geometry.Circle( offset_center, offset ),
                                                   geometry.Line( end, other_end ).perpendicular( offset_center ) )
    assert( len( vertices ) == 2 )
    return vertices


def vertices_for_sharp_corner( point1, center_point, point2, offset ):
    def vertice_for_one_corner_wall( corner_point, end_point, other_end_point ):
        vertices = vertices_for_line_segment_end( corner_point, end_point, offset )
        wall_line = geometry.Line( corner_point, end_point )
        if not wall_line.are_on_the_same_side( vertices[0], other_end_point ):
            return vertices[0]
        else:
            return vertices[1]

    return [ vertice_for_one_corner_wall( center_point, point1, point2 ),
             vertice_for_one_corner_wall( center_point, point2, point1 ) ]


def vertices_for_non_sharp_corner( point1, center_point, point2, offset ):
    def parallel_outstanding_line( corner, end, other_end ):
        corner_wall_line = geometry.Line( corner, end )
        perpendicular = corner_wall_line.perpendicular( corner )
        intersections = geometry.intersect_line_and_circle( geometry.Circle( corner, offset ), perpendicular )
        assert( len( intersections ) == 2 )
        if not corner_wall_line.are_on_the_same_side( intersections[0], other_end ):
            return perpendicular.perpendicular( intersections[0] )
        else:
            return perpendicular.perpendicular(intersections[1])

    outstanding_line1 = parallel_outstanding_line( center_point, point1, point2 )
    outstanding_line2 = parallel_outstanding_line( center_point, point2, point1 )
    return [ geometry.intersect_lines( outstanding_line1, outstanding_line2 ) ]


def is_corner_sharp( end_point1, center_point, end_point2 ):
    """Returns True if angle between lines end_point1-cetner_point
    and center_point-end_point2 is less then 90 degrees."""

    cathetus1 = geometry.Line( center_point, end_point1 )
    cathetus2 = cathetus1.perpendicular( end_point1 )
    hypotenuse = geometry.Line( center_point, end_point2 )

    cathetus2_intersection = geometry.intersect_lines( cathetus2, hypotenuse )

    if cathetus2_intersection is None:
        return False

    return cathetus1.are_on_the_same_side( end_point2, cathetus2_intersection )


def vertices_for_corner( point1, center_point, point2, offset ):
    if is_corner_sharp(point1, center_point, point2):
        return vertices_for_sharp_corner(point1, center_point, point2, offset)
    else:
        return vertices_for_non_sharp_corner(point1, center_point, point2, offset)


class PathWalker:
    def __init__(self, save_file = None):
        self.SAVE_FILE = "walls.json"

        self.SCREEN_SIZE = (1000, 625)

        self.VERTICE_SIZE = 3
        self.HIT_SIZE = 6

        self.BACKGROUND_COLOR = pygame.Color('white')
        self.WALL_COLOR = ( 0, 0, 0 )
        self.WALL_THICKNESS = 3
        self.NEW_WALL_SEGMENT_COLOR = ( 192, 192, 192 )
        self.NEW_WALL_THICKNESS = 1

        self.VERTICE_COLOR = ( 220, 220, 255 )
        self.EDGE_COLOR = ( 240, 240, 255 )

        self.QUAD_TREE_RECT_COLOR = ( 224, 232, 224 )

        self.WALKER_COLOR = ( 64, 192, 64 )
        self.WALKER_SIZE = 8
        self.WALKER_COMFORT_ZONE = self.WALKER_SIZE + 2
        self.WALKER_VERTICE_BUILDING_COMFORT_ZONE = self.WALKER_COMFORT_ZONE + 1

        self.REDRAW_RATE = 90

        self.alt_pressed = False
        self.shift_pressed = False
        self.ctrl_pressed = False

        self.show_pathfinding_graph = False
        self.show_quad_tree_rects = False

        self.walls = []
        self.quad_tree = None
        self.new_wall = None
        self.dragged_corner = None
        self.vertices = []
        self.edges = []
        self.quad_tree_rects = []

        self.walker_position = geometry.Point( 200, 200 )
        self.walker_path = None
        self.walker_path_position = None
        self.walker_speed_p_s = 160
        self.walker_last_move_time = None

        self.load_walls()

        self.redraw = True

    def load_walls(self):
        with open( self.SAVE_FILE ) as f:
            json_file = json.load( f )
            if "walls" in json_file:
                self.walls = [ [ geometry.Point( int( corner[0] ), int( corner[1] ) ) for corner in wall ] for wall in json_file["walls"] ]
            if "screen_size" in json_file:
                self.SCREEN_SIZE = json_file["screen_size"]

        # self.rebuild_pathfinding_graph()

    def save_walls(self):
        with open( self.SAVE_FILE, "w" ) as f:
            json.dump( { "screen_size" : self.SCREEN_SIZE,
                         "walls": [ [ ( corner.x, corner.y ) for corner in wall ] for wall in self.walls ] }, f )

    def redraw_screen(self, surface):
        surface.fill(self.BACKGROUND_COLOR)

        if self.show_quad_tree_rects:
            for rect in self.quad_tree_rects:
                pygame.draw.rect( surface, self.QUAD_TREE_RECT_COLOR, rect, 1 )

        if self.show_pathfinding_graph:
            for edge in self.edges:
                start = self.vertices[ edge[0] ].int_tuple( )
                end = self.vertices[ edge[1] ].int_tuple( )
                pygame.draw.line( surface, self.EDGE_COLOR, start, end )

            for vertice in self.vertices:
                pygame.draw.circle( surface, self.VERTICE_COLOR, vertice.int_tuple( ), self.VERTICE_SIZE )

        for wall in self.walls:
            for wall_segment in pairwise( wall ):
                pygame.draw.line( surface, self.WALL_COLOR, wall_segment[0].int_tuple( ), wall_segment[1].int_tuple( ),
                                  self.WALL_THICKNESS )

        if self.new_wall is not None:
            for i in range( 1, len( self.new_wall ) - 1 ):
                pygame.draw.line(surface, self.WALL_COLOR, self.new_wall[i-1].int_tuple(),
                                 self.new_wall[i].int_tuple(), self.NEW_WALL_THICKNESS)

            pygame.draw.line(surface, self.NEW_WALL_SEGMENT_COLOR, self.new_wall[-2].int_tuple(),
                             self.new_wall[-1].int_tuple(), self.NEW_WALL_THICKNESS)

        pygame.draw.circle(surface, self.WALKER_COLOR, ( int( self.walker_position.x ), int( self.walker_position.y ) ),
                           self.WALKER_SIZE)

        pygame.display.flip()

    def generate_vertices(self):
        offset = self.WALKER_VERTICE_BUILDING_COMFORT_ZONE

        for wall in self.walls:
            if len( wall ) > 2 and wall[0] == wall[-1]:
                self.vertices += vertices_for_corner( wall[1], wall[0], wall[-2], offset )
            else:
                self.vertices += vertices_for_line_segment_end( wall[0], wall[1], offset )
                self.vertices += vertices_for_line_segment_end( wall[-1], wall[-2], offset )

            for wall_corner in pairwise( pairwise( wall ) ):
                self.vertices += vertices_for_corner( wall_corner[0][0], wall_corner[0][1], wall_corner[1][1],
                                                      offset )

    def rebuild_quad_tree(self):
        self.quad_tree = QuadTree( geometry.BoundingBox( 0, self.SCREEN_SIZE[0], 0, self.SCREEN_SIZE[1] ), max_elems=4 )
        for wall in self.walls:
            for wall_segment in pairwise( wall ):
                self.quad_tree.add( geometry.LineSegment( wall_segment[0], wall_segment[1] ) )

        def get_quadrants_rects( quadrant ):
            if quadrant.subquadrants is not None:
                for subquadrant in quadrant.subquadrants:
                    get_quadrants_rects( subquadrant )
            else:
                self.quad_tree_rects.append( pygame.Rect( quadrant.bounding_box.x_lower, quadrant.bounding_box.y_lower,
                                                          quadrant.bounding_box.x_upper - quadrant.bounding_box.x_lower + 1,
                                                          quadrant.bounding_box.y_upper - quadrant.bounding_box.y_lower + 1 ) )

        get_quadrants_rects( self.quad_tree.main_quadrant )


    def rebuild_pathfinding_graph(self):
        self.quad_tree = None
        self.vertices = []
        self.edges = []
        start_time = time.time()
        self.generate_vertices()
        vertices_end_time = time.time()
        self.rebuild_quad_tree()
        quad_tree_end_time = time.time( )
        self.generate_edges()
        edges_end_time = time.time()
        print( "rebuilding pathfinding graph took {} seconds ({} for vertices, {} for quad tree and {} for edges)".format(
            edges_end_time-start_time,
            vertices_end_time-start_time,
            quad_tree_end_time-vertices_end_time,
            edges_end_time-quad_tree_end_time ) )

    def add_new_wall(self, wall):
        if len( wall ) == 3 and wall[0] == wall[-1]:
            wall = wall[0:2]
        self.walls.append( wall )

    def is_line_walkable(self, walk_line_segment):
        if self.quad_tree is None:
            return False

        start_circle = geometry.Circle( walk_line_segment.start, self.WALKER_COMFORT_ZONE )
        end_circle = geometry.Circle( walk_line_segment.end, self.WALKER_COMFORT_ZONE )

        start_points = geometry.intersect_line_and_circle( start_circle,
                                                           walk_line_segment.perpendicular( walk_line_segment.start ) )
        end_points = geometry.intersect_line_and_circle( end_circle,
                                                         walk_line_segment.perpendicular( walk_line_segment.end ) )

        if not walk_line_segment.are_on_the_same_side( start_points[0], end_points[0] ):
            end_points[0], end_points[1] = end_points[1], end_points[0]

        trajectory_bounding_rect_segments = [
            geometry.LineSegment( start_points[0], start_points[1] ),
            geometry.LineSegment( start_points[1], end_points[1] ),
            geometry.LineSegment( end_points[1], end_points[0] ),
            geometry.LineSegment( end_points[0], start_points[0] )
        ]

        potentially_interfering_walls = []
        for bounding_box in get_line_segment_bounding_boxes( walk_line_segment ):
            potentially_interfering_walls += self.quad_tree.get( bounding_box.expand( self.WALKER_COMFORT_ZONE + 1 ) )

        for wall_line_segment in potentially_interfering_walls:
            if ( does_line_segment_interfere_with_circle( wall_line_segment, start_circle ) or
                 does_line_segment_interfere_with_circle( wall_line_segment, end_circle ) ):
                return False

            if does_line_segment_interfere_with_rect( wall_line_segment, trajectory_bounding_rect_segments ):
                return False

        return True

    def generate_edges(self):
        for i in range( len( self.vertices ) ):
            for j in range( i+1, len( self.vertices ) ):
                new_edge = geometry.LineSegment( self.vertices[ i ], self.vertices[ j ] )

                if self.is_line_walkable( new_edge ):
                    self.edges.append( (i, j) )

    def handle_alt_shift_ctrl(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                self.shift_pressed = True
                return True
            elif event.key == pygame.K_RALT or event.key == pygame.K_LALT:
                self.alt_pressed = True
                return True
            elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                self.ctrl_pressed = True
                return True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                if self.new_wall is not None:
                    if len( self.new_wall ) > 2:
                        self.add_new_wall( self.new_wall[:-1] )
                    self.new_wall = None
                    self.redraw = True
                self.shift_pressed = False
                return True
            elif event.key == pygame.K_RALT or event.key == pygame.K_LALT:
                self.alt_pressed = False
                return True
            elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                self.ctrl_pressed = False
                return True

        return False

    def handle_mouse_move(self, event):
        if self.new_wall is not None:
            if check_hit( self.new_wall[0].int_tuple( ), event.pos, self.HIT_SIZE ):
                self.new_wall[-1] = self.new_wall[0]
            else:
                for wall in self.walls:
                    if wall[0] == wall[-1]:
                        continue
                    if check_hit( wall[0].int_tuple( ), event.pos, self.HIT_SIZE ):
                        self.new_wall[-1] = wall[0]
                        break
                    if check_hit(wall[-1].int_tuple(), event.pos, self.HIT_SIZE):
                        self.new_wall[-1] = wall[-1]
                        break
                else:
                    self.new_wall[-1] = geometry.Point( *event.pos )
            self.redraw = True
        elif self.dragged_corner is not None:
            wall = self.walls[ self.dragged_corner[0] ]
            if self.dragged_corner[1] == 0 and wall[0] == wall[-1]:
                wall[0] = wall[-1] = geometry.Point( *event.pos )
            else:
                wall[ self.dragged_corner[1] ] = geometry.Point( *event.pos )
            self.redraw = True

    def handle_mouse_down(self, event):
        if event.button == LEFT_MOUSE_BUTTON:
            if self.alt_pressed:
                pass
            elif self.ctrl_pressed:
                for i in range( len( self.walls ) ):
                    for j in range( len( self.walls[i] ) ):
                        if check_hit(self.walls[i][j].int_tuple(), event.pos, self.HIT_SIZE):
                            if j == 0 and self.walls[i][0] == self.walls[i][-1]:
                                # this is closed wall and we're removing first/last - "unclose" the wall
                                self.walls[i].pop(0)
                                self.walls[i].pop(-1)
                            elif j == 0 or j == len( self.walls[i] ) - 1:
                                # first or last - just remove it
                                self.walls[i].pop(j)
                                if len( self.walls[i] ) < 2:
                                    self.walls.pop( i )
                            else:
                                # remove an element in the middle
                                if self.walls[i][0] == self.walls[i][-1]:
                                    # if it is "closed" - unclose it
                                    self.walls[i] = self.walls[i][j+1:-1] + self.walls[i][0:j]
                                else:
                                    # not "closed" wall - break it into two
                                    if len( self.walls[i] ) - j - 1 >= 2:
                                        self.walls.append( self.walls[i][j+1:] )
                                    if j >= 2:
                                        self.walls[i] = self.walls[i][0:j]
                                    else:
                                        self.walls.pop( i )

                            self.redraw = True
                            return
            elif self.shift_pressed:
                if self.new_wall is None:
                    for i in range( len( self.walls ) ):
                        if check_hit( self.walls[i][0].int_tuple(), event.pos, self.HIT_SIZE ):
                            self.new_wall = list( reversed( self.walls.pop( i ) ) )
                            self.new_wall.append( geometry.Point( *event.pos ) )
                            break
                        elif check_hit( self.walls[i][-1].int_tuple(), event.pos, self.HIT_SIZE ):
                            self.new_wall = self.walls.pop( i )
                            self.new_wall.append( geometry.Point( *event.pos ) )
                            break
                    else:
                        self.new_wall = [ geometry.Point( *event.pos ), geometry.Point( *event.pos ) ]
                else:
                    if check_hit(self.new_wall[0].int_tuple(), event.pos, self.HIT_SIZE):
                        self.new_wall[-1] = self.new_wall[0]
                        self.add_new_wall(self.new_wall)
                        self.new_wall = None
                    else:
                        for i in range( len( self.walls ) ):
                            if self.walls[i][0] == self.walls[i][-1]:
                                continue

                            if check_hit(self.walls[i][0].int_tuple(), event.pos, self.HIT_SIZE):
                                self.walls[i] = self.new_wall[:-1] + self.walls[i]
                                self.new_wall = None
                                break

                            if check_hit(self.walls[i][-1].int_tuple(), event.pos, self.HIT_SIZE):
                                self.walls[i] = self.new_wall[:-1] + list( reversed( self.walls[i] ) )
                                self.new_wall = None
                                break

                        else:
                            self.new_wall[-1] = geometry.Point(*event.pos)
                            if self.new_wall[-2] != self.new_wall[-1]:
                                self.new_wall.append( geometry.Point( *event.pos ) )
                self.redraw = True
            else:
                for i in range( len( self.walls ) ):
                    for j in range( len( self.walls[i] ) ):
                        if check_hit(self.walls[i][j].int_tuple(), event.pos, self.HIT_SIZE):
                            self.dragged_corner = ( i, j )

        elif event.button == RIGHT_MOUSE_BUTTON:
            if self.alt_pressed:
                pass
            elif self.ctrl_pressed:
                print( "teleport", event.pos )
                self.stop_walk()
                self.walker_position = geometry.Point( *event.pos )
                self.redraw = True
            elif self.shift_pressed:
                pass
            else:
                start_time = time.time( )
                new_path = self.find_walk_path( geometry.Point( *event.pos ) )
                end_time = time.time( )
                print( "finding path took {} seconds".format( end_time-start_time ) )
                if new_path is not None:
                    self.walker_path = new_path
                    self.walker_path_position = 0
                    self.walker_last_move_time = time.time( )
                else:
                    self.stop_walk()

    def find_walk_path(self, dest):
        if self.is_line_walkable( geometry.LineSegment( self.walker_position, dest ) ):
            return [ self.walker_position, dest ]

        vertices = self.vertices + [ self.walker_position, dest ]
        vertice_count = len( vertices )
        edges = self.edges.copy( )
        for i in range( vertice_count - 2 ):
            if self.is_line_walkable( geometry.LineSegment( vertices[ i ], self.walker_position ) ):
                edges.append( ( i, vertice_count - 2 ) )
            if self.is_line_walkable( geometry.LineSegment( vertices[ i ], dest ) ):
                edges.append( ( i, vertice_count - 1 ) )

        graph = { i : dict( ) for i in range( len( vertices ) ) }
        for edge in edges:
            distance = geometry.distance( vertices[ edge[0] ], vertices[ edge[1] ] )
            graph[ edge[0] ][ edge[1] ] = distance
            graph[ edge[1] ][ edge[0] ] = distance

        start_time = time.time()
        path = pathfinder.find_cheapest_path_dijkstra( graph, vertice_count-2, vertice_count-1 )
        end_time = time.time()
        print( "dijkstra algorithm took {} seconds".format( end_time - start_time ) )
        if path is None:
            return None

        path_coordinates = [ vertices[ vertice_i ] for vertice_i in path["path"] ]
        return path_coordinates

    def stop_walk(self):
        self.walker_path = None
        self.walker_path_position = None
        self.walker_last_move_time = None

    def walk(self):
        if self.walker_path is None:
            return

        if self.walker_last_move_time is None:
            self.walker_last_move_time = time.time( )
            return

        current_time = time.time( )

        self.walker_path_position += ( current_time - self.walker_last_move_time ) * self.walker_speed_p_s

        current_leg_length = geometry.distance( self.walker_path[0], self.walker_path[1] )
        if self.walker_path_position >= current_leg_length:
            if len( self.walker_path ) == 2:
                self.walker_position = self.walker_path[1]
                self.stop_walk( )
                return
            else:
                self.walker_path_position -= current_leg_length
                self.walker_path.pop( 0 )

        self.walker_position = geometry.measure_out( self.walker_path[0], self.walker_path[1], self.walker_path_position )
        self.walker_last_move_time = current_time
        self.redraw = True

    def handle_mouse_up(self, event):
        if self.dragged_corner is not None:
            self.dragged_corner = None
            self.redraw = True

    def run(self):
        print( """brief help:
shift-click: add wall
click+drag: move corner
ctrl-click: remove corner
right-click: walk
ctrl-right-click: teleport
F2 - show/hide pathfinding graph
F3 - rebuild pathfinding graph
F4 - show/hide quad tree rects
""" )

        pygame.init()
        pygame.display.set_caption("path walker")
        screen = pygame.display.set_mode( self.SCREEN_SIZE )

        self.redraw_screen(screen)

        done = False

        while not done:
            self.redraw = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_move( event )

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down( event )

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up( event )

                elif self.handle_alt_shift_ctrl( event ):
                    pass

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F2:
                        self.show_pathfinding_graph = not self.show_pathfinding_graph
                        self.redraw = True
                    elif event.key == pygame.K_F3:
                        self.rebuild_pathfinding_graph()
                        self.redraw = True
                    elif event.key == pygame.K_F4:
                        self.show_quad_tree_rects = not self.show_quad_tree_rects
                        self.redraw = True

            if done:
                break

            self.walk()

            if not self.redraw:
                time.sleep( 1/self.REDRAW_RATE )
                continue

            screen.fill(self.BACKGROUND_COLOR)
            self.redraw_screen( screen )
            pygame.display.flip()

        self.save_walls()
        pygame.quit()


if __name__ == "__main__":
    walker = PathWalker( )
    walker.run( )
