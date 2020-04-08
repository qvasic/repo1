import json
import unittest

def find_cheapest_path_breadth( graph, start_id, end_id ):
    cheapest_path = None

    queue = [ { "cost": 0, "path": [ start_id ] } ]

    while len( queue ):
        current_path = queue.pop( 0 )

        last_vertex = current_path[ "path" ][ -1 ]
        if last_vertex == end_id:
            print("queue size", len(queue), "destination reached, possible route:", current_path, "current cheapest routes:", cheapest_path)
            if cheapest_path is None or cheapest_path["cost"] > current_path["cost"]:
                cheapest_path = current_path
            continue

        if cheapest_path is not None and cheapest_path["cost"] <= current_path["cost"]:
            continue

        for next_connected_vertex in graph[ last_vertex ]:
            if next_connected_vertex in current_path["path"]:
                continue

            queue.append( { "cost" : current_path["cost"] + graph[ last_vertex ][ next_connected_vertex ],
                            "path" : current_path["path"] + [ next_connected_vertex ] } )

    return cheapest_path

def find_cheapest_path( graph, start_id, end_id ):
    cheapest_path = None
    current_path = { "cost": 0, "path": [ start_id ] }

    def iterate_connections( node_id ):
        nonlocal cheapest_path
        if node_id == end_id:
            print( "destination reached, possible route:", current_path, "current cheapest routes:", cheapest_path )
            if not cheapest_path or cheapest_path["cost"] > current_path["cost"]:
                cheapest_path = current_path.copy( )
                cheapest_path["path"] = cheapest_path["path"].copy( )
            return

        if cheapest_path is not None and cheapest_path["cost"] <= current_path["cost"]:
            return

        connections = graph[ node_id ]
        for connected_node_id in connections:
            if connected_node_id in current_path["path"]:
                continue

            current_path["cost"] += connections[ connected_node_id ]
            current_path["path"].append( connected_node_id )

            iterate_connections( connected_node_id )

            current_path["path"].pop( )
            current_path["cost"] -= connections[ connected_node_id ]

    iterate_connections( start_id )
    return cheapest_path

class TestFindCheapestPath( unittest.TestCase ):

    with open( "graph.json" ) as f:
        graph = json.load( f )["graph"]

    def test_find_cheapest_path(self):
        self.assertEqual( find_cheapest_path( self.graph, "0", "1" ), { "cost": 10, "path": ["0", "1"] } )
        self.assertEqual( find_cheapest_path( self.graph, "0", "2" ), { "cost": 5, "path": ["0", "2"] } )
        self.assertEqual( find_cheapest_path( self.graph, "1", "2" ), { "cost": 5, "path": ["1", "2"] } )
        self.assertEqual( find_cheapest_path( self.graph, "0", "3" ), { "cost": 13, "path": ["0", "2", "3"] } )

    def test_find_cheapest_path_breadth(self):
        self.assertEqual( find_cheapest_path_breadth( self.graph, "0", "1" ), { "cost": 10, "path": ["0", "1"] } )
        self.assertEqual( find_cheapest_path_breadth( self.graph, "0", "2" ), { "cost": 5, "path": ["0", "2"] } )
        self.assertEqual( find_cheapest_path_breadth( self.graph, "1", "2" ), { "cost": 5, "path": ["1", "2"] } )
        self.assertEqual( find_cheapest_path_breadth( self.graph, "0", "3" ), { "cost": 13, "path": ["0", "2", "3"] } )


def main( ):
    print( "hell0 main" )

    unittest.main( )

    return


    with open( "graph.json" ) as f:
        graph = json.load( f )["graph"]
    print( graph )

    print( "0-1:", find_cheapest_path( graph, 0, 1 ) )
    #print( "0-2:", find_cheapest_path( graph, 0, 2 ) )
    #print( "1-2:", find_cheapest_path( graph, 1, 2 ) )
    #print( "0-3:", find_cheapest_path( graph, 0, 3 ) )

if __name__ == "__main__":
    main( )
