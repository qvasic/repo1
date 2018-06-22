import socket
import socketserver
import threading

PORT = 2222
FILE = "gps.log"
FREQ = 2

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
    
    global cur_line
    
    lat, lng = 0, 0
    
    while True:
        nmea_sent = ( nmea.gpgll( lat, lng ) + "\n" ).encode( "utf-8" )
        shared_gps_data.set( nmea_sent )
        lng += 0.1
        if lng > 180:
            lng -= 360
        time.sleep( 1/FREQ )
        #with open( FILE, "rb" ) as f:
        #    for l in f:
        #        shared_gps_data.set( l )
        #        time.sleep( 1/FREQ )

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
                    shared_printer.print( "ACTIVE connection from {}, {} lines sent"
                                                        .format( self.client_address, lines_sent ) )
                time.sleep( 1/FREQ )
        except KeyboardInterrupt:
            shared_printer.print( "USER ABORT" )
            self.server.shutdown()
        except Exception as e:
            shared_printer.print( "ERROR connection {}, exception: {}"
                                                                .format( self.client_address, e ) )


def main():
    file_reader_thread = threading.Thread( target=file_reader, daemon=True )
    file_reader_thread.start()

    srv = socketserver.ThreadingTCPServer( ( "", PORT ), CCPRequestHandler )
    shared_printer.print( "opened server on port {}, serving forever".format( PORT ) )
    srv.serve_forever()
    srv.server_close()

if __name__ == "__main__":
    main()
