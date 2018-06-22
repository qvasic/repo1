import socket
import socketserver
import threading

PORT = 2222
FILE = "gps.log"
FREQ = 1

class SharedData:
    """Shared data accessor class. Synchronizes gets and sets.
    Data should be immutable object, use set( ) to set new val, get( ) to get current val.
    """

    def __init__( self, init_val=None ):
        self.lock = threading.Lock( )
        self.data = init_val

    def get( self ):
        with self.lock:
            ret = self.data
        return ret

    def set( self, new_val ):
        with self.lock:
            self.data = new_val

class SharedPrinter:
    """Chared printer, synchronizes print operations."""

    def __init__( self ):
        self.lock = threading.Lock( )

    def print( self, to_print ):
        with self.lock:
            print( to_print )

def iter_by_n( iterable, N ):
    """Iterates by series of N elements.
    For instance given seqence [ 1, 2, 3, 4, 5 ], first iteration will give you [1, 2],
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


shared_gps_data = SharedData( b"" )
shared_printer = SharedPrinter( )

def file_reader():
    import time
    import nmea
    
    lat, lng = 0, 0
    
    while True:
        """
        nmea_sents = "{gpgga}\n{gpgsa}\n{gprmc}\n".format( gpgga=nmea.gpgga( lat, lng ), 
                                                           gpgsa=nmea.gpgsa( ), 
                                                           gprmc=nmea.gprmc( lat, lng ) ).encode( "utf-8" )
        shared_gps_data.set( nmea_sents )
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
                    shared_gps_data.set( cur_entry )
                    time.sleep( 1/FREQ )
                    line = 0

class CCPRequestHandler( socketserver.StreamRequestHandler ):
    def handle( self ):
        try:
            import time
            shared_printer.print( "NEW connection from {}".format( self.client_address ) )
            lines_sent = 0

            while True:
                self.wfile.write( shared_gps_data.get( ) )
                lines_sent += 1
                if lines_sent%100 == 0:
                    shared_printer.print( "ACTIVE connection from {}, {} entries sent"
                                                        .format( self.client_address, lines_sent ) )
                time.sleep( 1/FREQ )
        except Exception as e:
            shared_printer.print( "ERROR connection from {}, exception: {}"
                                                                .format( self.client_address, e ) )

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
