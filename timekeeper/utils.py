import time

def reset_time_of_day( original_time, hours, minutes, seconds = None ):
    """
    Given time (in seconds from epoch), modifies it so its hours/minutes are reset.
    """
    l = list( time.localtime( original_time ) )
    if seconds is not None:
        l[3:6] = [hours,minutes,seconds]
    else:
        l[3:5] = [hours,minutes]
    return time.mktime( time.struct_time( l ) )

def zero_seconds_of_today( ):
    return reset_time_of_day( time.time( ), 0, 0 )

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
