import socket
import socketserver
import threading

PORT = 2222
FILE = "gps.log"
FREQ = 1

cur_line = b""
cur_line_lock = threading.Lock()

def file_reader():
    import time
    import nmea
    
    global cur_line
    
    lat, lng = 0, 0
    
    while True:
        """
        nmea_sents = "{gpgga}\n{gpgsa}\n{gprmc}\n".format( gpgga=nmea.gpgga( lat, lng ), 
                                                           gpgsa=nmea.gpgsa( ), 
                                                           gprmc=nmea.gprmc( lat, lng ) ).encode( "utf-8" )
        with cur_line_lock:
            cur_line = nmea_sents
        lng += 0.1
        if lng > 180:
            lng -= 360
        time.sleep( 1/FREQ )
        """
        print( "ENGINE going through file {}".format( FILE ) )
        with open( FILE, "rb" ) as f:
            line = 0
            for l in f:
                if line == 0:
                    cur_entry = b""
                    
                cur_entry += l
                line += 1

                if line == 3:
                    with cur_line_lock:
                        cur_line = cur_entry
                    time.sleep( 1/FREQ )
                    line = 0

class CCPRequestHandler( socketserver.StreamRequestHandler ):
    def handle( self ):
        try:
            import time
            print( "NEW connection from {}".format( self.client_address ) )
            entries_sent = 0

            while True:
                with cur_line_lock:
                    self.wfile.write( cur_line )
                entries_sent += 1
                if entries_sent%100 == 0:
                    print( "ACTIVE connection from {}, {} entries sent".format( self.client_address,
                                                                              entries_sent ) )
                time.sleep( 1/FREQ )
        except Exception as e:
            print( "ERROR connection from {}, exception: {}".format( self.client_address, e ) )


def main():
    import sys
    
    if len( sys.argv ) > 1:
        global FILE
        FILE = sys.argv[1]

    file_reader_thread = threading.Thread( target=file_reader, daemon=True )
    file_reader_thread.start()

    srv = socketserver.ThreadingTCPServer( ( "", PORT ), CCPRequestHandler )
    print( "opened server on port {}, serving forever".format( PORT ) )
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print( "USER ABORT" )
    srv.server_close()

if __name__ == "__main__":
    main()
