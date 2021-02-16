import time
import flask
from timekeeper_db import get_timekeeper_db, DictAsObject
from utils import zero_seconds_of_today, format_time, epoch_into_local_time_of_day, seconds_into_hours_and_minutes, reset_time_of_day

app = flask.Flask( __name__ )

def convert_timesheets( timesheets ):
    day_beginning = zero_seconds_of_today( )
    now = int( time.time( ) )

    today_total = 0

    for t in timesheets:
        interval_in = max( ( t.time_start, day_beginning ) )
        interval_out = t.time_stop if t.time_stop else now
        interval_total = interval_out - interval_in
        today_total += interval_total

        t.time_start = epoch_into_local_time_of_day( t.time_start )
        t.time_stop = epoch_into_local_time_of_day( t.time_stop ) if t.time_stop else ""
        t.total = seconds_into_hours_and_minutes( interval_total )

    return seconds_into_hours_and_minutes( today_total )

def process_edit_form( form ):
    edited_data = dict( )
    for k in form:
        hyphen_position = k.find( "-" )
        if hyphen_position == -1:
            raise RuntimeError( "Field name error (no hyphen): " + k )

        try:
            timesheet_id = int( k[ hyphen_position + 1 : ] )
        except ValueError as e:
            raise RuntimeError( "Field name error (wrong timesheet id): " + k )

        if timesheet_id not in edited_data:
            edited_data[ timesheet_id ] = dict( )
            
        if k.startswith( "start" ):
            edited_data[ timesheet_id ][ "time_start" ] = flask.request.form[ k ]
        elif k.startswith( "stop" ):
            edited_data[ timesheet_id ][ "time_stop" ] = flask.request.form[ k ]
        else:
            raise RuntimeError( "Field name error (wrong prefix): " + k )

    return [ DictAsObject( { "timesheet_id" : timesheet_id, 
                             "time_start" : edited_data[ timesheet_id ][ "time_start" ], 
                             "time_stop" : edited_data[ timesheet_id ][ "time_stop" ] } ) 
             for timesheet_id in edited_data ]

def parse_time_groups( time_str ):
    """Parses time string, with hours and minutes, like 18:45.
    Also checks that value are in proper range.
    If something is wrong - raises ValueError exception.
    If everything is right - return tuple of two integers: hours and minutes."""
    time_groups = time_str.split( ":" )
    if len( time_groups ) != 2:
        raise ValueError( "Wrong number of time groups, must be two: hours and minutes." )
    return tuple( int( group ) for group in time_groups )    

def reset_time_of_day_from_time_str( seconds_from_epoch, time_str ):
    time_groups = parse_time_groups( time_str )
    return reset_time_of_day( seconds_from_epoch, *time_groups )

def verify_and_convert_edit_form( form ):
    timekeeper_db = get_timekeeper_db( )
    converted = []
    for i, item in zip( range( len( form ) ), form ):
        original_timesheet = timekeeper_db.get_timesheet( item.timesheet_id )
        if not original_timesheet:
            raise RuntimeError( "Wrong timesheet id." )

        try:
            original_timesheet.time_start = reset_time_of_day_from_time_str( original_timesheet.time_start, item.time_start )
            if item.time_stop != "":
                original_timesheet.time_stop = reset_time_of_day_from_time_str( original_timesheet.time_stop, item.time_stop )
            elif i < len( form ) -1:
                raise RuntimeError( "Only last interval can be open." )
        except ValueError as e:
            raise RuntimeError( "Could not parse time: " + str( e ) )

        converted.append( original_timesheet )

    return converted

def check_session( f ):
    def decorator( ):
        timekeeper_db = get_timekeeper_db( )
        session = None
        if "session_id" in flask.request.args:
            session_id = flask.request.args["session_id"]
            session = timekeeper_db.get_session( session_id )
        
        if session is None:
            return flask.render_template( "redirect.html", target="login", message="Session error. Click here to re-login." )

        if session.expiration_time < time.time( ):
            return flask.render_template( "redirect.html", target="login", message="Session expired. Click here to re-login." )

        return f( session )

    decorator.__name__ = "check_session_for_" + f.__name__

    return decorator

@app.route( "/", methods=[ "GET" ] )
@app.route( "/login", methods=['GET'] )
def login_page( ):
    return flask.render_template( "login.html" )

@app.route( "/login", methods=['POST'] )
def do_login( ):
    timekeeper_db = get_timekeeper_db( )

    username = flask.request.form["username"]
    password = flask.request.form["password"]

    if timekeeper_db.login( username, password ):
        session_id = timekeeper_db.create_new_session( username )
        return flask.render_template( "redirect.html", target=( "time?session_id=" + str( session_id ) ), message="Login sucessfull. Click here to continue." )
    else:
        return flask.render_template( "login.html", error_message="login failed" )    

@app.route( "/time", methods=['GET', 'POST'] )
@check_session
def time_page( session ):
    timekeeper_db = get_timekeeper_db( )

    if flask.request.method == 'POST':
        timekeeper_db.start_stop_timesheet( session.username )

    timesheets = timekeeper_db.get_timesheets_for_today( session.username )
    today_total = convert_timesheets( timesheets )

    return flask.render_template( "time.html", timesheets = timesheets, today_total = today_total, 
                                  session_id = session.session_id, username = session.username )

@app.route( "/edit", methods=[ "GET", "POST" ] )
@check_session
def edit_page( session ):
    timekeeper_db = get_timekeeper_db( )
    timesheets = timekeeper_db.get_timesheets_for_today( session.username )
    today_total = convert_timesheets( timesheets )

    message = None

    if flask.request.method == 'POST':
        try:
            timesheets = process_edit_form( flask.request.form )
            processed_timesheets = verify_and_convert_edit_form( timesheets )
            message = "not implemented yet\nform: " + str( timesheets ) + "\nprocessed: " + str( processed_timesheets )

        except RuntimeError as e:
            message = "edit form processing error: " + str( e )
        

    return flask.render_template( "edit.html", timesheets = timesheets, session_id = session.session_id, username = session.username, message = message )
