import json
import sys
import random


def generate_mesh_graph( width, height, start_pos = [ 10, 10 ], spacing = 30, rnd = 5 ):
    graph = { "vertices" : [], "edges" : [] }

    def get_vertice_id( x, y ):
        return y * width + x

    def gen_vertice_pos( x, y ):
        return [ start_pos[0] + x * spacing + ( random.randint( -rnd, rnd ) ),
                 start_pos[1] + y * spacing + ( random.randint( -rnd, rnd ) ) ]

    def connect( v1, v2, bidirectional=True ):
        graph["edges"].append( [ get_vertice_id( *v1 ), get_vertice_id( *v2 ) ] )
        if bidirectional:
            graph["edges"].append( [ get_vertice_id( *v2 ), get_vertice_id( *v1 ) ] )

    for i in range( height - 1 ):
        for j in range( width ):
            graph["vertices"].append( gen_vertice_pos( j, i ) )

            connect( ( j, i ), ( j, i+1 ) )

            if j > 0:
                connect((j, i), (j-1, i + 1))

            if j < width-1:
                connect((j, i), (j+1, i))
                connect((j, i), (j+1, i+1))

    for j in range( width ):
        graph["vertices"].append( gen_vertice_pos( j, height - 1 ) )
        if j < width-1:
            connect((j, height - 1), (j + 1, height - 1))

    return graph


def main( ):
    graph = generate_mesh_graph( 17, 11, ( 30, 30 ), 70 )
    json.dump( graph, sys.stdout )


if __name__ == "__main__":
    main( )
