import time
import flask
from timekeeper_db import get_timekeeper_db
from utils import beginning_of_the_day, format_time, epoch_into_local_time_of_day, seconds_into_hours_and_minutes

app = flask.Flask( __name__ )

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

def check_session( f ):
    def decorator( ):
        timekeeper_db = get_timekeeper_db( )
        session = None
        if "session_id" in flask.request.args:
            session_id = flask.request.args["session_id"]
            session = timekeeper_db.get_session( session_id )
        
        if session is None:
            return flask.render_template( "redirect.html", target="login", message="Session error. Click here to re-login." )

        if session["expiration_time"] < time.time( ):
            return flask.render_template( "redirect.html", target="login", message="Session expired. Click here to re-login." )

        return f( session )

    return decorator

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
        timekeeper_db.start_stop_timesheet( session["username"] )

    timesheets = timekeeper_db.get_timesheets( session["username"] )
    today_total = convert_timesheets( timesheets )

    return flask.render_template( "time.html", timesheets = timesheets, today_total = today_total, session_id = session["session_id"], username = session[ "username" ] )

#@app.route( "/edit", methods=[ "GET", "POST" ] )
#@check_session
#def edit_page( session ):
#    return "hell"
