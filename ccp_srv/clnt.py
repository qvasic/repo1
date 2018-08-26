"ccp client, connects to a server and get nmea sentences from it"

def main():
    print( __file__, __doc__ )

    import socket, sys

    addr = "localhost" if len( sys.argv ) == 1 else sys.argv[1]

    s = socket.create_connection( ( addr, 2222 ) )
    print( "reading from server" )
    for l in s.makefile( 'r' ):
        print( l, end="" )


if __name__ == "__main__":
    main()
