"ccp client, connects to a server and get nmea sentences from it"

def avg( iterable ):
    sum = 0
    count = 0
    for i in iterable:
        sum += i
        count += 1
    return sum/count

def main():
    print( __file__, __doc__ )

    import socket, sys, time
    from srv_file import iter_by_n

    addr = "localhost" if len( sys.argv ) == 1 else sys.argv[1]

    s = socket.create_connection( ( addr, 2222 ) )
    print( "profiling server" )
    
    batch = []
    batch_max = 10
    prev_timestamp = time.time( )
    for l in iter_by_n( s.makefile( 'r' ), 9 ):
        curr_timestamp = time.time( )
        batch.append( curr_timestamp-prev_timestamp )
        if len( batch ) == batch_max:
            print( "min={:5.3}, max={:5.3}, avg={:5.3}".format( min( batch ), max( batch ), avg( batch ) ), 
                   *( round( item, 3 ) for item in batch ), 
                   flush=True )
            batch = []
        prev_timestamp = curr_timestamp


if __name__ == "__main__":
    main()
