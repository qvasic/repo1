import socket
import socketserver

PORT = 2222
FILE = "gps.log"
FREQ = 10

class CCPRequestHandler( socketserver.StreamRequestHandler ):
    def handle( self ):
        try:
            import time
            print( "connection from {}".format( self.client_address ) )
            print( "sending lines from {} with frequency {}".format( FILE, FREQ ) )
            lines_sent = 0
            with open( FILE, "rb" ) as f:
                for l in f:
                    self.wfile.write( l )
                    lines_sent += 1
                    print( "\r{} lines sent".format( lines_sent ), end="" )
                    time.sleep( 1/FREQ )
                print()
        except KeyboardInterrupt:
            self.server.shutdown()

def main():
    srv = socketserver.TCPServer( ( "", PORT ), CCPRequestHandler )
    print( "opened server on port {}, serving forever".format( PORT ) )
    srv.serve_forever()
    srv.server_close()

if __name__ == "__main__":
    main()
