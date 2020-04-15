"""
TODO:
- figure out inheritance and eq operators in geometry module
- add bounding box check to intersect_line_segments
- put geometry and pathfinder in separate module in separate project to be used by other projects
- implement is_line_walkable for walkers with size
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
        self.walker_speed_p_s = 120
        self.walker_last_move_time = None

        self.redraw = True

    def draw_arrow(self, screen, start, end, color = ( 0, 0, 0 ), width = 1):
        ARROW_ANGLE = 30
        ARROW_LENGTH = 5

        if start == end:
            return

        pygame.draw.line(screen, color, start, end, width )
        angle = geometry.angle( start[0] - end[0], start[1] - end[1] )

        arrow_center_coords = ( (end[0] + start[0]) / 2, (end[1] + start[1]) / 2 )
        for edge_angle in ( ARROW_ANGLE, -ARROW_ANGLE ):
            arrow_edge = geometry.coords( angle + edge_angle, ARROW_LENGTH )
            pygame.draw.line(screen, color, arrow_center_coords,
                             ( arrow_edge[0] + arrow_center_coords[0],
                               arrow_edge[1] + arrow_center_coords[1] ), width )

    def redraw_screen(self, surface):
        surface.fill(self.BACKGROUND_COLOR)

        for edge in self.edges:
            start = int( self.vertices[ edge[0] ].x ), int( self.vertices[ edge[0] ].y )
            end = int( self.vertices[ edge[1] ].x ), int( self.vertices[ edge[1] ].y )
            pygame.draw.line( surface, self.EDGE_COLOR, start, end )

        for vertice in self.vertices:
            pygame.draw.circle( surface, self.VERTICE_COLOR, ( int( vertice.x ), int( vertice.y ) ), self.VERTICE_SIZE )

        for wall in self.walls:
            pygame.draw.line( surface, self.WALL_COLOR, wall[0], wall[1], self.WALL_THICKNESS )

        if self.new_wall is not None:
            pygame.draw.line(surface, self.NEW_WALL_COLOR, self.new_wall[0], self.new_wall[1])

        pygame.draw.circle(surface, self.WALKER_COLOR, ( int( self.walker_position.x ), int( self.walker_position.y ) ),
                           self.WALKER_SIZE)

        pygame.display.flip()

    def generate_vertices(self):
        OFFSET_LEN = 10

        self.vertices = []
        for wall in self.walls:
            offset_centers = []
            wall_line = geometry.Line( geometry.Point( *wall[0] ), geometry.Point( *wall[1] ) )
            if wall_line.vertical:
                if wall[0][1] > wall[1][1]:
                    wall[0], wall[1] = wall[1], wall[0]
                offset_centers = [ geometry.Point( wall_line.x, wall[0][1] - OFFSET_LEN ),
                                   geometry.Point( wall_line.x, wall[1][1] + OFFSET_LEN ) ]
            else:
                if wall[0][0] > wall[1][0]:
                    wall[0], wall[1] = wall[1], wall[0]
                x_offset = OFFSET_LEN / math.sqrt( wall_line.a ** 2 + 1 )

                left_x = wall[0][0] - x_offset
                right_x = wall[1][0] + x_offset
                offset_centers = [ geometry.Point( left_x, left_x * wall_line.a + wall_line.b ),
                                   geometry.Point( right_x, right_x * wall_line.a + wall_line.b ) ]

            for offset_center in offset_centers:
                perpendicular = wall_line.perpendicular( offset_center )
                intersections = geometry.intersect_line_and_circle( geometry.Circle( offset_center, OFFSET_LEN ),
                                                                    perpendicular )

                self.vertices += intersections

    def is_line_walkable(self, line_segment):
        for wall in self.walls:
            wall_line_segment = geometry.LineSegment(geometry.Point(wall[0][0], wall[0][1]),
                                                     geometry.Point(wall[1][0], wall[1][1]))
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
                self.shift_pressed = False
            elif event.key == pygame.K_RALT or event.key == pygame.K_LALT:
                self.alt_pressed = False
            elif event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL:
                self.ctrl_pressed = False
            return True

        return False

    def handle_mouse_move(self, event):
        if self.new_wall is not None:
            self.new_wall[1] = event.pos
            self.redraw = True

    def handle_mouse_down(self, event):
        if event.button == LEFT_MOUSE_BUTTON:
            if self.alt_pressed:
                pass
            elif self.ctrl_pressed:
                pass
            elif self.shift_pressed:
                self.new_wall = [ event.pos, event.pos ]
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
        if event.button == LEFT_MOUSE_BUTTON:
            if self.new_wall is not None:
                self.walls.append( self.new_wall )
                self.new_wall = None
                self.generate_vertices()
                self.generate_edges()
                self.redraw = True

                print( "new wall", self.walls[-1] )
                print(len(self.vertices), "vertices", self.vertices)
                print( len( self.edges ), "edges", self.edges )

    def run(self):
        print( """brief help:
shift-click+drag: add wall
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