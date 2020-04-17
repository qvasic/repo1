"""
DONE:
- put geometry and pathfinder in separate module in separate project to be used by other projects
- figure out inheritance and eq operators in geometry module
- generate vertices only outside of angles
- change creating walls into sequence of walls


TODO:
- add bounding box check to intersect_line_segments
- intersection of line segments which are on the same line

- implement is_line_walkable for walkers with size

- creation of "closed" walls
- corner cases for vertices generation - "not corner" corner, 0-degrees angle corner

- debug absent edges - new wall [Point( 58, 48 ), Point( 58, 418 ), Point( 460, 439 ), Point( 464, 387 ), Point( 102, 375 ), Point( 103, 318 ), Point( 726, 357 ), Point( 715, 461 ), Point( 526, 449 ), Point( 517, 479 ), Point( 30, 460 ), Point( 27, 18 ), Point( 106, 20 ), Point( 98, 264 ), Point( 722, 306 ), Point( 722, 306 )]
"""


import pygame
import math
import time
import geometry
import pathfinder

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
    return geometry.intersect_lines( outstanding_line1, outstanding_line2 )


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


class PathWalker:
    def __init__(self, save_file = None):
        self.VERTICE_SIZE = 4
        self.HIT_SIZE = self.VERTICE_SIZE + 2

        self.BACKGROUND_COLOR = pygame.Color('white')
        self.WALL_COLOR = ( 0, 0, 0 )
        self.WALL_THICKNESS = 3
        self.NEW_WALL_COLOR = ( 192, 192, 192 )

        #self.VERTICE_COLOR = ( 0, 0, 255 )
        #self.EDGE_COLOR = ( 192, 192, 255 )
        self.VERTICE_COLOR = ( 220, 220, 255 )
        self.EDGE_COLOR = ( 240, 240, 255 )

        self.WALKER_COLOR = ( 64, 192, 64 )
        self.WALKER_SIZE = 5

        self.REDRAW_RATE = 90

        self.alt_pressed = False
        self.shift_pressed = False
        self.ctrl_pressed = False

        self.walls = []
        self.new_wall = None
        self.vertices = []
        self.edges = []

        self.walker_position = geometry.Point( 200, 200 )
        self.walker_path = None
        self.walker_path_position = None
        self.walker_speed_p_s = 160
        self.walker_last_move_time = None

        self.redraw = True

    def redraw_screen(self, surface):
        surface.fill(self.BACKGROUND_COLOR)

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
            for new_wall_segment in pairwise( self.new_wall ):
                pygame.draw.line(surface, self.NEW_WALL_COLOR, new_wall_segment[0].int_tuple( ),
                                 new_wall_segment[1].int_tuple( ))

        pygame.draw.circle(surface, self.WALKER_COLOR, ( int( self.walker_position.x ), int( self.walker_position.y ) ),
                           self.WALKER_SIZE)

        pygame.display.flip()

    def generate_vertices(self):
        OFFSET_LEN = 10

        self.vertices = []
        for wall in self.walls:
            self.vertices += vertices_for_line_segment_end( wall[0], wall[1], OFFSET_LEN )
            self.vertices += vertices_for_line_segment_end( wall[-1], wall[-2], OFFSET_LEN )
            for wall_corner in pairwise( pairwise( wall ) ):
                if is_corner_sharp( wall_corner[0][0], wall_corner[0][1], wall_corner[1][1] ):
                    self.vertices += vertices_for_sharp_corner( wall_corner[0][0], wall_corner[0][1], wall_corner[1][1],
                                                                OFFSET_LEN )
                else:
                    self.vertices.append( vertices_for_non_sharp_corner( wall_corner[0][0], wall_corner[0][1],
                                                                         wall_corner[1][1], OFFSET_LEN ) )

    def is_line_walkable(self, line_segment):
        for wall in self.walls:
            for wall_segment in pairwise( wall ):
                wall_line_segment = geometry.LineSegment( wall_segment[0], wall_segment[1] )
                if geometry.intersect_line_segments(line_segment, wall_line_segment) is not None:
                    return False

        return True

    def generate_edges(self):
        self.edges = []
        for i in range( len( self.vertices ) ):
            for j in range( i+1, len( self.vertices ) ):
                new_edge = geometry.LineSegment( self.vertices[ i ], self.vertices[ j ] )
                if self.is_line_walkable( new_edge ):
                    self.edges.append( (i, j) )

    def handle_alt_shift_ctrl(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                self.shift_pressed = True
            elif event.key == pygame.K_RALT or event.key == pygame.K_LALT:
                self.alt_pressed = True
            elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                self.ctrl_pressed = True
            return True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                if self.new_wall is not None:
                    if len( self.new_wall ) > 2:
                        print( "new wall", self.new_wall )
                        self.walls.append( self.new_wall[:-1] )
                        self.generate_vertices()
                        self.generate_edges()
                    self.new_wall = None
                    self.redraw = True
                self.shift_pressed = False
            elif event.key == pygame.K_RALT or event.key == pygame.K_LALT:
                self.alt_pressed = False
            elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                self.ctrl_pressed = False
            return True

        return False

    def handle_mouse_move(self, event):
        if self.new_wall is not None:
            self.new_wall[-1] = geometry.Point( *event.pos )
            self.redraw = True

    def handle_mouse_down(self, event):
        if event.button == LEFT_MOUSE_BUTTON:
            if self.alt_pressed:
                pass
            elif self.ctrl_pressed:
                pass
            elif self.shift_pressed:
                if self.new_wall is None:
                    self.new_wall = [ geometry.Point( *event.pos ), geometry.Point( *event.pos ) ]
                else:
                    if self.new_wall[-2] != self.new_wall[-1]:
                        self.new_wall[-1] = geometry.Point( *event.pos )
                        self.new_wall.append( geometry.Point( *event.pos ) )
                self.redraw = True
            else:
                pass
        elif event.button == RIGHT_MOUSE_BUTTON:
            if self.alt_pressed:
                pass
            elif self.ctrl_pressed:
                self.stop_walk()
                self.walker_position = geometry.Point( *event.pos )
                self.redraw = True
            elif self.shift_pressed:
                pass
            else:
                new_path = self.find_walk_path( geometry.Point( *event.pos ) )
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

        path = pathfinder.find_cheapest_path_dijkstra( graph, vertice_count-2, vertice_count-1 )
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
        None

    def run(self):
        print( """brief help:
shift-click: add wall
right-click: walk
ctrl-right-click: teleport
""" )

        pygame.init()
        pygame.display.set_caption("path walker")
        screen = pygame.display.set_mode((800, 500))

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

            if done:
                break

            self.walk()

            if not self.redraw:
                time.sleep( 1/self.REDRAW_RATE )
                continue

            screen.fill(self.BACKGROUND_COLOR)
            self.redraw_screen( screen )
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    walker = PathWalker( )
    walker.run( )