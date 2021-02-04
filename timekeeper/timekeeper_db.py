import sqlite3
import time
from utils import beginning_of_the_day

def fetchall_as_dicts( cursor ):
    """Fetches all from an sqlite3 cursor and converts each element into dict with column name as dict keys."""
    return [ { k[0] : v for v, k in zip( row, cursor.description ) }
             for row in cursor.fetchall( ) ]

class TimeKeeperDB:
    def __init__( self, db_filename ):
        self.connection = sqlite3.connect( db_filename )

    def login( self, username, password ):
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

        return session_select_result_list[ 0 ]

    def get_timesheets( self, username ):
        cursor = self.connection.cursor( )
        day_beginning = beginning_of_the_day( )
        cursor.execute( "SELECT time_start, time_stop FROM timesheets WHERE username = ? AND ( time_stop IS NULL OR time_stop > ? )", ( username, day_beginning ) )
        return [ { "in" : row[0], "out" : row[1] } for row in cursor ]

    def start_stop_timesheet( self, username ):
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