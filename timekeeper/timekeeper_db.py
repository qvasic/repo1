import sqlite3
import time
from utils import zero_seconds_of_today

class DictAsObject:
    """Transforms a dict into an object with corresponding attributes:
    DictAsObject( { "one" : 1 } ) => obj with one attribute: o.one."""

    def __init__( self, d ):
        for k in d:
            self.__dict__[ k ] = d[ k ]

    def __str__( self ):
        return "DictAsObject dict=" + str( self.__dict__ )

    def __repr__( self ):
        return str( self )

def fetchall_as_dicts( cursor ):
    """Fetches all from an sqlite3 cursor and converts each element into dict with column name as dict keys."""
    return [ { k[0] : v for v, k in zip( row, cursor.description ) }
             for row in cursor.fetchall( ) ]

class TimeKeeperDB:
    def __init__( self, db_filename ):
        self.connection = sqlite3.connect( db_filename )

    def login( self, username, password ):
        """Logs in existing user or creates new user. Returns true or false, depending on the success of the operation."""

        cursor = self.connection.cursor( )
        cursor.execute( "SELECT password FROM users WHERE username = ?", ( username, ) )
        result_list = fetchall_as_dicts( cursor )
        if ( len( result_list ) != 1 ):
            cursor.execute( "INSERT INTO users ( username, password ) VALUES ( ? , ? )", ( username, password ) )
            self.connection.commit( )
            return True
        else:
            return result_list[ 0 ][ "password" ] == password

    def create_new_session( self, username ):
        """Creates new session for a given user. Return new session's id."""

        SESSION_EXPIRATION_SECONDS = 60 * 180
        now = int( time.time( ) )
        expiration = now + SESSION_EXPIRATION_SECONDS

        cursor = self.connection.cursor( )
        cursor.execute( "INSERT INTO sessions ( username, ip_address, login_time, expiration_time ) VALUES ( ? , ? , ? , ? )", ( username, "ip_address", now, expiration ) )
        self.connection.commit( )
        return cursor.lastrowid

    def get_session( self, session_id ):
        """Returns session info for given session id. Session object contains username, ip_address, login and expiration times."""
        cursor = self.connection.cursor( )
        cursor.execute( "SELECT username, ip_address, login_time, expiration_time, session_id FROM sessions WHERE session_id = ?", ( session_id, ) )

        session_select_result_list = fetchall_as_dicts( cursor )
        if ( len( session_select_result_list ) != 1 ):
            return None

        return DictAsObject( session_select_result_list[ 0 ] )

    def get_timesheets_for_today( self, username ):
        """Return list of timesheets for today."""

        cursor = self.connection.cursor( )
        day_beginning = zero_seconds_of_today( )
        cursor.execute( "SELECT time_start, time_stop, timesheet_id FROM timesheets WHERE username = ? AND ( time_stop IS NULL OR time_stop > ? )", ( username, day_beginning ) )
        return [ DictAsObject( item ) for item in fetchall_as_dicts( cursor ) ]

    def get_timesheet( self, timesheet_id ):
        """Returns timesheet object for a given id."""
        cursor = self.connection.cursor( )
        cursor.execute( "SELECT time_start, time_stop, timesheet_id FROM timesheets WHERE timesheet_id = ?", ( timesheet_id, ) )
        select_result = [ DictAsObject( item ) for item in fetchall_as_dicts( cursor ) ]
        if not select_result:
            return None
        return select_result[ 0 ]

    def update_timesheet( self, timesheet_id, time_start, time_stop ):
        """Updates a timesheet with given id."""

        cursor = self.connection.cursor( )
        cursor.execute( "UPDATE timesheets time_start = ? , time_end = ? WHERE timewheet_id = ?", ( time_start, time_end, timesheet_id ) )
        self.connection.commit( )

    def start_stop_timesheet( self, username ):
        """Closes existing timesheet or opens new one."""

        cursor = self.connection.cursor( )
        cursor.execute( "SELECT timesheet_id, time_stop FROM timesheets WHERE username = ? and time_start = ( SELECT MAX( time_start ) FROM timesheets WHERE username = ? ) LIMIT 1", ( username, username ) )
        last_timesheet_list = fetchall_as_dicts( cursor )
        assert( len( last_timesheet_list ) <= 1 );
        now = int( time.time( ) )
        if len( last_timesheet_list ) == 1 and last_timesheet_list[0][ "time_stop" ] is None:
            cursor.execute( "UPDATE timesheets SET time_stop = ? WHERE timesheet_id = ?", ( now, last_timesheet_list[0][ "timesheet_id" ] ) )
        else:
            cursor.execute( "INSERT INTO timesheets ( username, time_start ) VALUES ( ? , ? )", ( username, now ) )

        self.connection.commit( )

def get_timekeeper_db( ):
    return TimeKeeperDB( "timekeeper.db" )