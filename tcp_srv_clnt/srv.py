import socket
import socketserver

PORT = 10443
FILE = "gps.log"
FREQ = 10

class CCPRequestHandler( socketserver.StreamRequestHandler ):
    def handle( self ):
        import time

        print( "connection from {}".format( self.client_address ) )
        print( "sending lines from {} with frequency {}".format( FILE, FREQ ) )

        with open( FILE, "rb" ) as f:
            for l in f:
                self.wfile.write( l )
                time.sleep( 1/FREQ )

def main():
    srv = socketserver.TCPServer( ( "", PORT ), CCPRequestHandler )
    print( "opened server on port {}, serving forever".format( PORT ) )
    srv.serve_forever()

if __name__ == "__main__":
    main()
