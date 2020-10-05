def parse_elevator_movements( seq ):
    initial_unknown = 0
    for i in range( len( seq ) ):
        if seq[ i ] != -1:
            initial_unknown = i
            break

    groups = [ { "sequence" : [], "trailing_unknown" : 0  } ]
    previous_known = True
    for i in range( initial_unknown, len( seq ) ):
        if previous_known:
            if seq[ i ] != -1:
                groups[ -1 ][ "sequence" ].append( seq[ i ] )
            else:
                groups[ -1 ][ "trailing_unknown" ] += 1
                previous_known = False
        else:
            if seq[ i ] != -1:
                groups.append( { "sequence" : [ seq[ i ] ], "trailing_unknown" : 0  } )
                previous_known = True
            else:
                groups[ -1 ][ "trailing_unknown" ] += 1

    return { "initial_unknown" : initial_unknown, "groups" : groups }
                


def read_test( ):
    M, N = ( int( n ) for n in input( ).split( ) )
    elevator_movements = list( int( n ) for n in input( ).split( ) )
    print( M, N )
    print( elevator_movements )
    print( parse_elevator_movements( elevator_movements ) )

def main( ):
    T = int( input( ) )
    for t in range( T ):
        read_test( )

if __name__ == "__main__":
    main( )
