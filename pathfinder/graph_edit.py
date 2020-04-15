import pygame
import json
import math
import geometrics
import time
import pathfinder
import sys

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

class GraphEditor:
    def __init__(self, save_file = None):
        self.SAVE_FILE = "graph_edit.json" if not save_file else save_file

        self.VERTICE_SIZE = 4
        self.SELECTED_VERTICE_SIZE = 6
        self.HIT_SIZE = self.VERTICE_SIZE + 2

        self.BACKGROUND_COLOR = pygame.Color('white')
        self.VERTICE_COLOR = ( 192, 0, 0 )
        self.SELECTED_VERTICE_COLOR = ( 255, 0, 0 )
        self.EDGE_COLOR = ( 128, 128, 128 )
        self.SELECTED_EDGE_COLOR = ( 0, 0, 0 )

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
            if i in self.selected_vertices:
                pygame.draw.circle(screen, self.SELECTED_VERTICE_COLOR, vertice, self.SELECTED_VERTICE_SIZE)
            else:
                pygame.draw.circle(screen, self.VERTICE_COLOR, vertice, self.VERTICE_SIZE)

    def draw_arrow(self, screen, start, end, color = ( 0, 0, 0 ), width = 1):
        EDGE_ANGLE = 30
        EDGE_LENGTH = 5

        if start == end:
            return

        pygame.draw.line(screen, color, start, end, width )
        angle = geometrics.angle( start[0] - end[0], start[1] - end[1] )

        arrow_center_coords = ( (end[0] + start[0]) / 2, (end[1] + start[1]) / 2 )
        for edge_angle in ( EDGE_ANGLE, -EDGE_ANGLE ):
            arrow_edge = geometrics.coords( angle + edge_angle, EDGE_LENGTH )
            pygame.draw.line(screen, color, arrow_center_coords,
                             ( arrow_edge[0] + arrow_center_coords[0],
                               arrow_edge[1] + arrow_center_coords[1] ), width )

    def draw_edges(self, screen):
        for edge in self.edges:
            self.draw_arrow(screen, self.vertices[edge[0]], self.vertices[edge[1]], self.EDGE_COLOR, 1)

        for path_edge in self.path_edges:
            self.draw_arrow(screen, self.vertices[path_edge[0]], self.vertices[path_edge[1]], self.SELECTED_EDGE_COLOR, 3)
        return

    def draw_data(self, screen):
        self.draw_edges( screen )
        self.draw_vertices( screen )
        if self.dragging_new_edge_from_vertice_i is not None and self.new_edge_end_pos:
            self.draw_arrow(screen, self.vertices[self.dragging_new_edge_from_vertice_i],
                            self.new_edge_end_pos)
        # pixelate(screen, 5)

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

    def handle_mouse_move(self, event):
        if self.dragging_vertice_i is not None:
            self.vertices[self.dragging_vertice_i] = list(event.pos)
            self.redraw = True
        elif self.dragging_new_edge_from_vertice_i is not None:
            self.new_edge_end_pos = list(event.pos)
            self.redraw = True

    def handle_mouse_down(self, event):
        if event.button == LEFT_MOUSE_BUTTON:
            if self.alt_pressed:
                self.vertices.append(list(event.pos))
                self.redraw = True
            elif self.ctrl_pressed:
                vertice_i = self.find_vertice_by_pos(event.pos)
                if vertice_i is not None:
                    self.remove_vertice(vertice_i)
                    self.selected_vertices.clear()
                    self.path_edges.clear()
                    self.redraw = True
                else:
                    edge_i = self.find_edge_by_center_pos(event.pos)
                    if edge_i is not None:
                        self.edges.pop(edge_i)
                        self.redraw = True
            elif self.shift_pressed:
                vertice_i = self.find_vertice_by_pos(event.pos)
                if vertice_i is not None:
                    self.dragging_new_edge_from_vertice_i = vertice_i
            else:
                self.dragging_vertice_i = self.find_vertice_by_pos(event.pos)
        elif event.button == RIGHT_MOUSE_BUTTON:
            vertice_i = self.find_vertice_by_pos(event.pos)
            if vertice_i is not None:
                if len(self.selected_vertices) >= 2:
                    self.selected_vertices.clear()
                    self.path_edges.clear()
                self.selected_vertices.append(vertice_i)

                if len(self.selected_vertices) == 2:
                    graph = self.generate_pathfinder_input_data()
                    print(graph)

                    time_start = time.time()
                    path = pathfinder.find_cheapest_path_dijkstra(graph,
                                                                  self.selected_vertices[0],
                                                                  self.selected_vertices[1])
                    time_end = time.time()

                    print(path)
                    print("pathfinding took", time_end - time_start)

                    if path is not None and "path" in path and len(path["path"]) > 1:
                        for i in range(len(path["path"]) - 1):
                            self.path_edges.append([path["path"][i], path["path"][i + 1]])

                self.redraw = True

    def handle_mouse_up(self, event):
        if event.button == LEFT_MOUSE_BUTTON:
            self.dragging_vertice_i = None
            if self.dragging_new_edge_from_vertice_i is not None:
                end_vertice_i = self.find_vertice_by_pos(event.pos)
                if end_vertice_i is not None and end_vertice_i != self.dragging_new_edge_from_vertice_i:
                    new_edge = [self.dragging_new_edge_from_vertice_i, end_vertice_i]
                    if new_edge not in self.edges:
                        self.edges.append([self.dragging_new_edge_from_vertice_i, end_vertice_i])
                self.dragging_new_edge_from_vertice_i = None
                self.redraw = True

    def run(self):
        print( """brief help:
alt+click: add new vertice
ctrl+click: remove existing vertice
click+drag: move existing vertice
shift+click+draw: added new edge between vertices
right-click: select a vertice as start or end
""" )
        self.dragging_new_edge_from_vertice_i = None
        self.new_edge_end_pos = None

        pygame.init()
        pygame.display.set_caption("graph edit")
        screen = pygame.display.set_mode((1200, 800))
        screen.fill(self.BACKGROUND_COLOR)
        self.draw_data( screen )
        pygame.display.flip()

        done = False

        self.dragging_vertice_i = None

        self.redraw = False

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

            if not self.redraw:
                time.sleep( 1/self.UPDATE_RATE )
                continue

            screen.fill(self.BACKGROUND_COLOR)
            self.draw_data( screen )
            pygame.display.flip()

        self.save_graph()
        pygame.quit()

if __name__ == "__main__":
    if len( sys.argv ) > 1:
        editor = GraphEditor( sys.argv[1] )
    else:
        editor = GraphEditor( )
    editor.run( )