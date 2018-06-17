"tcp client, connects to a server and sends a stream of something to it"

def main():
    print( __file__, __doc__ )

    import socket
    import time

    s = socket.create_connection( ( "127.0.0.1", 10443 ) )
    f = s.makefile( 'w' )
    for i in range( 20 ):
        print( i, file=f, flush=True )
        time.sleep( 0.3 )


if __name__ == "__main__":
    main()
