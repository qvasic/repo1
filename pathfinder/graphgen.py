import pygame
import json
import math
import geometrics

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
        self.HIT_SIZE = self.VERTICE_SIZE + 2
        self.BLACK = pygame.Color('black')
        self.BACKGROUND = pygame.Color('white')
        self.RED = pygame.Color('red')

        self.alt_pressed = False
        self.shift_pressed = False
        self.ctrl_pressed = False

        self.vertices = []
        self.edges = []

        self.load_graph( )

    def load_graph(self):
        with open( self.SAVE_FILE ) as save_file:
            graph_json_obj = json.load( save_file )
            self.vertices = graph_json_obj["vertices"]
            self.edges = graph_json_obj["edges"]

    def save_graph(self):
        with open( self.SAVE_FILE, "w" ) as save_file:
            json.dump( { "vertices" : self.vertices, "edges" : self.edges }, save_file )

    def draw_vertices(self, screen):
        for vertice in self.vertices:
            pygame.draw.circle(screen, self.RED, vertice, self.VERTICE_SIZE)

    def draw_arrow(self, screen, start, end):
        EDGE_ANGLE = 25
        EDGE_LENGTH = 9
        EDGE_WIDTH = 1

        if start == end:
            return

        pygame.draw.line(screen, self.BLACK, start, end, 1 )
        angle = geometrics.angle( start[0] - end[0], start[1] - end[1] )
        for arrow_coords in ( end, ( ( end[0] + start[0] ) / 2, ( end[1] + start[1] ) / 2 ) ):
            for edge_angle in ( EDGE_ANGLE, -EDGE_ANGLE ):
                arrow_edge = geometrics.coords( angle + edge_angle, EDGE_LENGTH )
                pygame.draw.line(screen, self.BLACK, arrow_coords,
                                 ( arrow_edge[0] + arrow_coords[0],
                                   arrow_edge[1] + arrow_coords[1] ), EDGE_WIDTH )

    def draw_edges(self, screen):
        for edge in self.edges:
            self.draw_arrow( screen, self.vertices[ edge[0] ], self.vertices[ edge[1] ] )

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
                    if event.button == 1:
                        if self.alt_pressed:
                            self.vertices.append(event.pos)
                            redraw = True
                        elif self.ctrl_pressed:
                            vertice_i = self.find_vertice_by_pos( event.pos )
                            if vertice_i is not None:
                                self.remove_vertice( vertice_i )
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


                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
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