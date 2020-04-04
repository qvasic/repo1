import json
import unittest

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

        connections = graph[ node_id ]
        for connected_node_id in connections:
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
