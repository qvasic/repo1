import flask
app = flask.Flask( __name__ )

import sqlite3
import time

def beginning_of_the_day( ):
    l = list( time.localtime( time.time( ) ) )
    l[3:6] = [0,0,0]
    return time.mktime( time.struct_time( l ) )

class TimeKeeperDB:
    def __init__( self, db_filename ):
        self.connection = sqlite3.connect( db_filename )

    def login( self, username, password ):
        cursor = self.connection.cursor( )
        cursor.execute( "SELECT password FROM users WHERE username = ?", ( username, ) )
        result_list = cursor.fetchall( )
        if ( len( result_list ) != 1 ):
            cursor.execute( "INSERT INTO users ( username, password ) VALUES ( ? , ? )", ( username, password ) )
            self.connection.commit( )
            return True
        else:
            return result_list[ 0 ][ 0 ] == password

    def create_new_session( self, username ):
        now = int( time.time( ) )
        expiration = now + 60 * 10

        cursor = self.connection.cursor( )
        cursor.execute( "INSERT INTO sessions ( username, ip_address, login_time, expiration_time ) VALUES ( ? , ? , ? , ? )", ( username, "ip_address", now, expiration ) )
        self.connection.commit( )
        return cursor.lastrowid

    def get_session( self, session_id ):
        cursor = self.connection.cursor( )
        cursor.execute( "SELECT username, ip_address, login_time, expiration_time FROM sessions WHERE session_id = ?", ( session_id, ) )
        result_list = cursor.fetchall( )
        if ( len( result_list ) != 1 ):
            return None

        return { "username" : result_list[0][0], "ip_address" : result_list[0][1], "login_time" : result_list[0][2], "expiration_time" : result_list[0][3] }

    def get_timesheets( self, username ):
        cursor = self.connection.cursor( )
        day_beginning = beginning_of_the_day( )
        cursor.execute( "SELECT time_start, time_stop FROM timesheets WHERE username = ? AND ( time_stop IS NULL OR time_stop > ? )", ( username, day_beginning ) )
        return [ { "in" : row[0], "out" : row[1] } for row in cursor ]

    def start_stop_timesheet( self, username ):
        cursor = self.connection.cursor( )
        cursor.execute( "SELECT timesheet_id, time_stop FROM timesheets WHERE username = ? and time_start = ( SELECT MAX( time_start ) FROM timesheets WHERE username = ? ) LIMIT 1", ( username, username ) )
        last_timesheet_list = cursor.fetchall( )
        assert( len( last_timesheet_list ) <= 1 );
        now = int( time.time( ) )
        if len( last_timesheet_list ) == 1 and last_timesheet_list[0][1] is None:
            cursor.execute( "UPDATE timesheets SET time_stop = ? WHERE timesheet_id = ?", ( now, last_timesheet_list[0][0] ) )
        else:
            cursor.execute( "INSERT INTO timesheets ( username, time_start ) VALUES ( ? , ? )", ( username, now ) )

        self.connection.commit( )

def format_time( hours, minutes ):
    return "{}:{}".format( hours, minutes )

def epoch_into_local_time_of_day( seconds_since_epoch ):
    t = time.localtime( seconds_since_epoch )
    return format_time( t.tm_hour, t.tm_min )

def seconds_into_hours_and_minutes( seconds ):
    seconds_in_hour = 3600
    seconds_in_minute = 60
    hours = int( seconds // seconds_in_hour )
    minutes = int( ( seconds - hours * seconds_in_hour ) // seconds_in_minute )
    return format_time( hours, minutes )

def convert_timesheets( timesheets ):
    day_beginning = beginning_of_the_day( )
    now = int( time.time( ) )

    today_total = 0

    for t in timesheets:
        interval_in = max( ( t["in"], day_beginning ) )
        interval_out = t["out"] if t["out"] else now
        interval_total = interval_out - interval_in
        today_total += interval_total

        t["in"] = epoch_into_local_time_of_day( t["in"] )
        t["out"] = epoch_into_local_time_of_day( t["out"] ) if t["out"] else ""
        t["total"] = seconds_into_hours_and_minutes( interval_total )

    return seconds_into_hours_and_minutes( today_total )

timekeeper_db = TimeKeeperDB( "timekeeper.db" )

@app.route( "/login", methods=['GET'] )
def login_page( ):
    return flask.render_template( "login.html" )

@app.route( "/login", methods=['POST'] )
def do_login( ):
    username = flask.request.form["username"]
    password = flask.request.form["password"]

    if timekeeper_db.login( username, password ):
        session_id = timekeeper_db.create_new_session( username )
        return flask.render_template( "redirect.html", target=( "timekeeper?session_id=" + str( session_id ) ), message="Login sucessfull. Click here to continue." )
    else:
        return flask.render_template( "login.html", error_message="login failed" )    

@app.route( "/timekeeper", methods=['GET', 'POST'] )
def timekeeper_page( ):
    session = None
    if "session_id" in flask.request.args:
        session_id = flask.request.args["session_id"]
        session = timekeeper_db.get_session( session_id )
    
    if session is None:
        return flask.render_template( "redirect.html", target="login", message="Session error. Click here to re-login." )

    if session["expiration_time"] < time.time( ):
        return flask.render_template( "redirect.html", target="login", message="Session expired. Click here to re-login." )

    if flask.request.method == 'POST':
        timekeeper_db.start_stop_timesheet( session["username"] )

    timesheets = timekeeper_db.get_timesheets( session["username"] )
    today_total = convert_timesheets( timesheets )

    return flask.render_template( "timekeeper.html", timesheets = timesheets, today_total = today_total, session_id = session_id, username = session[ "username" ] )
