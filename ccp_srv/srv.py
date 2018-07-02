import socket
import socketserver
import threading

class SharedData:
    """Shared data accessor class. Synchronizes gets and sets.
    Data should be immutable object - otherwise sync it yourself!
    Use set( ) to set new val, get( ) to get current val.
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

shared_printer = SharedPrinter( )

def createCCPRequestHandler( shared_bin_data, freq, event_stop ):
    """Creates new handler class for TCP server.
    Will send binary data which is stored in shared_bin_data freq times per second, until event_stop
    is set.

    Also, some crazy Python b******t going on here.
    This function creates a new parametrized class.
    This class refers local variables of this function, this is super weird for people not
    closely familiar with Python. Every separate function execution creates separate
    execution context object, which contains all local objects created during function execution.
    Class created in this context have a reference to this "execution context object", so as long
    class object exists, context object will exist as well.
    Basically I am writing this for myself N years from now. Hello, your old f****r!
    """

    class CCPRequestHandler( socketserver.StreamRequestHandler ):
        def handle( self ):
            try:
                import time
                shared_printer.print( "NEW connection from {}".format( self.client_address ) )
                lines_sent = 0

                while not event_stop.is_set( ):
                    self.wfile.write( shared_bin_data.get( ) )
                    lines_sent += 1
                    if lines_sent%100 == 0:
                        shared_printer.print( "ACTIVE connection from {}, {} entries sent"
                                                        .format( self.client_address, lines_sent ) )
                    time.sleep( 1/freq )
                else:
                    shared_printer.print( "END connection from {}, server stops"
                                                                    .format( self.client_address ) )
            except Exception as e:
                shared_printer.print( "ERROR connection from {}, exception: {}"
                                                                .format( self.client_address, e ) )
    return CCPRequestHandler

class CCPServer:
    """Creates Current Car Position server in a separate thread bind to port port.
    shared_bin_nmea - instance of SharedData object, expected to contain binary NMEA sentences,
    but basically can contain any binary data, they will be sent with frequency freq
    to every client connected.

    Tupical modus operandi is as follows: create SharedData object, create CCPServer object with it,
    start server, set shared data to whatever you want, server will send it to any client connected,
    once you're done (for instance when user clicks "Exit" button, or when KeyboardInterrupt arrives,
    stop the server.
    """

    def __init__( self, shared_bin_nmea, freq=1, port=2222 ):
        self.port = port
        self.srv_stops = threading.Event( )
        self.srv = socketserver.ThreadingTCPServer( ( "", port ),
                                                    createCCPRequestHandler( shared_bin_nmea,
                                                                             freq,
                                                                             self.srv_stops )
                                                  )
        self.thread = threading.Thread( target=self.srv.serve_forever )

    def start( self ):
        """Starts the server in separate thread and returns."""
        self.thread.start( )
        shared_printer.print( "CCP SERVER port {} STARTS".format( self.port ) )

    def stop( self ):
        """Stops the server, wait for it to shutdown, also asks all handlers to stop as well."""
        shared_printer.print( "CCP SERVER port {} STOPS".format( self.port ) )
        self.srv_stops.set( )
        self.srv.shutdown( )
        self.thread.join( )
        self.srv.server_close( )

if __name__ == "__main__":
    print( "contains Current Car Position Server class, should be used as a module" )
