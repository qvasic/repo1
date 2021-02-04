import time

def beginning_of_the_day( ):
    l = list( time.localtime( time.time( ) ) )
    l[3:6] = [0,0,0]
    return time.mktime( time.struct_time( l ) )

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
