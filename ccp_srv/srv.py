import socket
import socketserver
import threading

PORT = 2222
FILE = "gps.log"
FREQ = 2

cur_line = b""
cur_line_lock = threading.Lock()

def file_reader():
    import time
    import nmea
    
    global cur_line
    
    lat, lng = 0, 0
    
    while True:
        nmea_sent = ( nmea.gpgll( lat, lng ) + "\n" ).encode( "utf-8" )
        with cur_line_lock:
            cur_line = nmea_sent
        lng += 0.1
        if lng > 180:
            lng -= 360
        time.sleep( 1/FREQ )
        #with open( FILE, "rb" ) as f:
        #    for l in f:
        #        with cur_line_lock:
        #            cur_line = l
        #        time.sleep( 1/FREQ )

class CCPRequestHandler( socketserver.StreamRequestHandler ):
    def handle( self ):
        try:
            import time
            print( "NEW connection from {}".format( self.client_address ) )
            lines_sent = 0

            while True:
                with cur_line_lock:
                    self.wfile.write( cur_line )
                lines_sent += 1
                if lines_sent%100 == 1:
                    print( "ACTIVE connection from {}, {} lines sent".format( self.client_address,
                                                                              lines_sent ) )
                time.sleep( 1/FREQ )
        except KeyboardInterrupt:
            print( "USER ABORT" )
            self.server.shutdown()
        except Exception as e:
            print( "ERROR connection {}, exception: {}".format( self.client_address, e ) )


def main():
    file_reader_thread = threading.Thread( target=file_reader, daemon=True )
    file_reader_thread.start()

    srv = socketserver.ThreadingTCPServer( ( "", PORT ), CCPRequestHandler )
    print( "opened server on port {}, serving forever".format( PORT ) )
    srv.serve_forever()
    srv.server_close()

if __name__ == "__main__":
    main()
