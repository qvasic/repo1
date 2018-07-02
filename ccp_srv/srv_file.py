"""Opens file gps.log or other file passed as first argument, iterates it by three lines at once
(created with NMEA sentences GPGGA, GPGSA and GPRMC in mind, but can be anything), once a second
sends those lines to anyone who connects to port 2222.
Iteration goes on even if no one is connected, so this can be useful to emulate vehicle movement
even when navigation system is off, rebooting, etc.
"""

def iter_by_n( iterable, N ):
    """Iterates by series of N elements.
    For instance given seqence [ 1, 2, 3, 4, 5 ] with N=2, first iteration will give you [1, 2],
    second [3, 4], and third and final - [5].
    """
    n=0
    for i in iterable:
        if n == 0:
            curr_iter = []
        curr_iter.append( i )
        n+=1
        if n == N:
            yield curr_iter
            n=0

    if n != 0:
        yield curr_iter

def main():
    import time, sys, srv

    if len( sys.argv ) > 1:
        filename = sys.argv[1]
    else:
        filename = "gps.log"

    shared_nmea_data = srv.SharedData( b"" )
    server = srv.CCPServer( shared_nmea_data )
    server.start( )

    try:
        while True:
            print( "MAIN LOOP going through file {}".format( filename ) )
            with open( filename, "rb" ) as f:
                for e in iter_by_n( f, 3 ):
                    gps_data = b"".join( e )
                    shared_nmea_data.set( gps_data );
                    time.sleep( 1 )
    except KeyboardInterrupt:
        print( "MAIN LOOP USER ABORT" )
    finally:
        server.stop( )

if __name__ == "__main__":
    main()
