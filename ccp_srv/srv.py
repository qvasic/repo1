import socket
import socketserver
import threading

PORT = 2222
FILE = None
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
    """Shared printer, synchronizes print operations."""

    def __init__( self ):
        self.lock = threading.Lock( )

    def print( self, to_print ):
        with self.lock:
            print( to_print )

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

class EarthCircumventor:
    def __init__( self, coords_setter_callback=None ):
        """coords_setter_callback - callback function that will update systems's current position.
        Expects arguments: latitude, longitude, speed in m/s, current bearing."""
        self.update_coords = coords_setter_callback

    def run( self ):
        import earth_walk, time

        speed_m_s = 1000
        speed_deg = earth_walk.Earth_dist_to_deg( speed_m_s )

        lat, lng = 0, 0
        bearing = 30

        while True:
            prev_lat, prev_lng = lat, lng
            lat, lng = earth_walk.step( lat, lng, bearing, speed_deg/FREQ )
            bearing = ( earth_walk.dist_and_brng( lat, lng, prev_lat, prev_lng )[1]+180 ) % 360

            if self.update_coords:
                self.update_coords( lat, lng, speed_m_s, bearing )

            time.sleep( 1/FREQ )

shared_gps_data = SharedData( b"" )
shared_printer = SharedPrinter( )

def coords_generator():
    import time, nmea, driver
    
    if FILE:
        while True:
            print( "ENGINE going through file {}".format( FILE ) )
            with open( FILE, "rb" ) as f:
                for e in iter_by_n( f, 3 ):
                    gps_data = b"".join( e )
                    shared_gps_data.set( gps_data );
                    time.sleep( 1/FREQ )
    else:
        print( "ENGINE no file given, simulating Earth circumvention" )

        def update_coords_shared( lat, lng, speed_m_s, bearing ):
            nmea_sents = nmea.gpgga_gpgsa_gprmc( lat, lng, nmea.meters_to_knots( 3600*speed_m_s ),
                                                 bearing ).encode( "utf-8" )
            shared_gps_data.set( nmea_sents )

        #circumvent = EarthCircumventor( update_coords_shared )
        #circumvent.run( )

        drvr = driver.Driver( update_coords_shared )
        drvr.run( )

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

    coords_generator_thread = threading.Thread( target=coords_generator, daemon=True )
    coords_generator_thread.start()

    srv = socketserver.ThreadingTCPServer( ( "", PORT ), CCPRequestHandler )
    print( "opened server on port {}, serving forever".format( PORT ) )
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print( "USER ABORT" )
    srv.server_close()

if __name__ == "__main__":
    main()
