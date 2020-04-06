import pygame
import json
import math
import geometrics
import time
import pathfinder

LEFT_MOUSE_BUTTON = 1
RIGHT_MOUSE_BUTTON = 3

def distance( p1, p2 ):
    return math.sqrt( ( p1[0]-p2[0] ) ** 2 + ( p1[1]-p2[1] ) ** 2 )

def check_hit( pos, hit, hit_size ):
    if (pos[0] - hit_size <= hit[0] and hit[0] <= pos[0] + hit_size
        and pos[1] - hit_size <= hit[1] and hit[1] <= pos[1] + hit_size):
        if distance(pos, hit) <= hit_size:
            return True

    return False

class GraphEditor:
    def __init__(self):
        self.SAVE_FILE = "graphgen.json"
        self.VERTICE_SIZE = 4
        self.SELECTED_VERTICE_SIZE = 6
        self.HIT_SIZE = self.VERTICE_SIZE + 2
        self.BLACK = pygame.Color('black')
        self.BACKGROUND = pygame.Color('white')
        self.RED = pygame.Color('red')
        self.UPDATE_RATE = 90

        self.alt_pressed = False
        self.shift_pressed = False
        self.ctrl_pressed = False

        self.vertices = []
        self.edges = []

        self.selected_vertices = []
        self.path_edges = []

        self.load_graph( )

    def generate_pathfinder_input_data(self):
        graph = dict( )

        for i in range( len( self.vertices ) ):
            graph[ i ] = { edge[1] : distance( self.vertices[ i ], self.vertices[ edge[ 1 ] ] )
                           for edge in filter( lambda e : e[0] == i, self.edges ) }

        return graph

    def load_graph(self):
        with open( self.SAVE_FILE ) as save_file:
            graph_json_obj = json.load( save_file )
            self.vertices = graph_json_obj["vertices"]
            self.edges = graph_json_obj["edges"]

    def save_graph(self):
        with open( self.SAVE_FILE, "w" ) as save_file:
            json.dump( { "vertices" : self.vertices, "edges" : self.edges }, save_file )

    def draw_vertices(self, screen):
        for i in range( len( self.vertices ) ):
            vertice = self.vertices[i]
            pygame.draw.circle(screen, self.RED, vertice,
                               self.VERTICE_SIZE if i not in self.selected_vertices else self.SELECTED_VERTICE_SIZE)

    def draw_arrow(self, screen, start, end, bold = False):
        EDGE_ANGLE = 25
        EDGE_LENGTH = 9
        EDGE_WIDTH = 1 if not bold else 2

        #print( "draw arrow", start, end )

        if start == end:
            return

        pygame.draw.line(screen, self.BLACK, start, end, EDGE_WIDTH )
        angle = geometrics.angle( start[0] - end[0], start[1] - end[1] )
        for arrow_coords in ( end, ( ( end[0] + start[0] ) / 2, ( end[1] + start[1] ) / 2 ) ):
            for edge_angle in ( EDGE_ANGLE, -EDGE_ANGLE ):
                arrow_edge = geometrics.coords( angle + edge_angle, EDGE_LENGTH )
                pygame.draw.line(screen, self.BLACK, arrow_coords,
                                 ( arrow_edge[0] + arrow_coords[0],
                                   arrow_edge[1] + arrow_coords[1] ), EDGE_WIDTH )

    def draw_edges(self, screen):
        for i in range( len( self.edges ) ):
            edge = self.edges[i]
            self.draw_arrow( screen, self.vertices[ edge[0] ], self.vertices[ edge[1] ],
                             edge in self.path_edges )

    def draw_data(self, screen):
        self.draw_edges( screen )
        self.draw_vertices( screen )

    def find_vertice_by_pos(self, pos):
        for i, vertice in zip( range( len( self.vertices ) ), self.vertices ):
            if check_hit( vertice, pos, self.HIT_SIZE ):
                return i

        return None

    def find_edge_by_center_pos(self, pos):
        for i in range( len( self.edges ) ):
            edge = self.edges[ i ]
            center = ( ( self.vertices[ edge[0] ][0] + self.vertices[ edge[1] ][0] ) / 2,
                       ( self.vertices[ edge[0] ][1] + self.vertices[ edge[1] ][1] ) / 2 )
            if check_hit( pos, center, self.HIT_SIZE ):
                return i

        return None

    def remove_vertice(self, vertice_i):
        i = 0
        while i < len( self.edges ):
            edge = self.edges[ i ]
            if edge[0] == vertice_i or edge[1] == vertice_i:
                self.edges.pop( i )
                continue
            if edge[0] > vertice_i:
                edge[0] -= 1
            if edge[1] > vertice_i:
                edge[1] -= 1

            i += 1

        self.vertices.pop( vertice_i )

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

    def run(self):
        print( """brief help:
alt+click: add new vertice
ctrl+click: remove existing vertice
click+drag: move existing vertice
shift+click+draw: added new edge between vertices
right-click: select a vertice as start or end
""" )

        pygame.init()
        pygame.display.set_caption("graph")
        screen = pygame.display.set_mode((800, 600))
        screen.fill(self.BACKGROUND)
        self.draw_data( screen )
        pygame.display.flip()

        done = False

        dragging_vertice_i = None

        dragging_new_edge_from_vertice_i = None
        new_edge_end_pos = None

        while not done:
            redraw = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

                elif event.type == pygame.MOUSEMOTION:
                    if dragging_vertice_i is not None:
                        self.vertices[ dragging_vertice_i ] = list( event.pos )
                        redraw = True
                    elif dragging_new_edge_from_vertice_i is not None:
                        new_edge_end_pos = list( event.pos )
                        redraw = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == LEFT_MOUSE_BUTTON:
                        if self.alt_pressed:
                            self.vertices.append( list( event.pos ) )
                            redraw = True
                        elif self.ctrl_pressed:
                            vertice_i = self.find_vertice_by_pos( event.pos )
                            if vertice_i is not None:
                                self.remove_vertice( vertice_i )
                                self.selected_vertices.clear( )
                                self.path_edges.clear( )
                                redraw = True
                            else:
                                edge_i = self.find_edge_by_center_pos( event.pos )
                                if edge_i is not None:
                                    self.edges.pop( edge_i )
                                    redraw = True
                        elif self.shift_pressed:
                            vertice_i = self.find_vertice_by_pos( event.pos )
                            if vertice_i is not None:
                                dragging_new_edge_from_vertice_i = vertice_i
                        else:
                            dragging_vertice_i = self.find_vertice_by_pos( event.pos )
                    elif event.button == RIGHT_MOUSE_BUTTON:
                        vertice_i = self.find_vertice_by_pos( event.pos )
                        if vertice_i is not None:
                            if len( self.selected_vertices ) >= 2:
                                self.selected_vertices.clear( )
                                self.path_edges.clear( )
                            self.selected_vertices.append( vertice_i )

                            if len( self.selected_vertices ) == 2:
                                graph = self.generate_pathfinder_input_data()
                                print( graph )

                                time_start = time.time( )
                                path = pathfinder.find_cheapest_path( graph,
                                                                      self.selected_vertices[0],
                                                                      self.selected_vertices[1] )
                                time_end = time.time( )

                                print( path )
                                print( "pathfinding took", time_end - time_start )

                                if path is not None and "path" in path and len( path["path"] ) > 1:
                                    for i in range( len( path["path"] ) - 1 ):
                                        self.path_edges.append( [ path["path"][ i ], path["path"][ i + 1 ] ] )

                            redraw = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == LEFT_MOUSE_BUTTON:
                        dragging_vertice_i = None
                        if dragging_new_edge_from_vertice_i is not None:
                            end_vertice_i = self.find_vertice_by_pos( event.pos )
                            if end_vertice_i is not None and end_vertice_i != dragging_new_edge_from_vertice_i:
                                new_edge = [ dragging_new_edge_from_vertice_i, end_vertice_i ]
                                if new_edge not in self.edges:
                                    self.edges.append( [ dragging_new_edge_from_vertice_i, end_vertice_i ] )
                            dragging_new_edge_from_vertice_i = None
                            redraw = True


                elif self.handle_alt_shift_ctrl( event ):
                    pass

            if done:
                break

            if not redraw:
                time.sleep( 1/self.UPDATE_RATE )
                continue

            screen.fill(self.BACKGROUND)
            self.draw_data( screen )
            if dragging_new_edge_from_vertice_i is not None and new_edge_end_pos:
                self.draw_arrow( screen, self.vertices[ dragging_new_edge_from_vertice_i ],
                                 new_edge_end_pos )
            pygame.display.flip()

        self.save_graph()
        pygame.quit()

if __name__ == "__main__":
    editor = GraphEditor( )
    editor.run( )