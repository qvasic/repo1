import time
import sqlite3
import eway

# if time between vehicle position records exceed this time - 
# vehicle is considered temporary off route
OFFROUTE_TIME = 59

# if new point's index is smaller than previous' - 
# it means vehicle start route over
# but sometimes there are gps glitches and it can appear that vehicle backtracked
# to filter this out we have a limit on how many points can vehicle jump over, 
# if it started the route over
RESTART_LIMIT = 10

def get_day( t, day_start_hour = 3 ):
    """Returns tuple with first and one-after-last seconds of the route working day, 
    which include time t."""

    # mktime      struct_time -> <seconds from Epoch>
    # localtime   <seconds from Epoch> -> struct_time

    t_expanded = list( time.localtime( t ) )
    if t_expanded[3] < day_start_hour:
        start = list( t_expanded )
        start[3:6] = ( 0, 0, 0 )
        start = time.struct_time( start )
        start = list( time.localtime( time.mktime( start )-1 ) )
        start[3:6] = (day_start_hour, 0, 0 )
        start = time.mktime( time.struct_time( start ) )

        end = list( t_expanded )
        end[3:6] = ( day_start_hour, 0, 0 )
        end = time.mktime( time.struct_time( end ) )

        return ( start, end )
    else:
        start = list( t_expanded )
        start[3:6] = ( day_start_hour, 0, 0 )
        start = time.mktime( time.struct_time( start ) )

        end = list( t_expanded )
        end[3:6] = ( 23, 59, 59 )
        end = time.struct_time ( end )
        end = list( time.localtime( time.mktime( end )+1 ) )
        end[3:6] = ( day_start_hour, 0, 0 )
        end = time.mktime( time.struct_time( end ) )

        return ( start, end )

class ewaystat:
    def __init__( self ):
        self.conn = sqlite3.connect( "data/eway.db" )

    def add_vehicle_pass( route_point, vehicle_id, pass_time ):
        if "vehicle_passes" not in route_point:
            route_point["vehicle_passes"] = []
        pass_time_struct = time.localtime( pass_time )
        pass_time_in_day = ( pass_time_struct.tm_hour*60*60 + 
                            pass_time_struct.tm_min*60 +
                            pass_time_struct.tm_sec )
        route_point["vehicle_passes"].append( {"vehicle_id":vehicle_id, "time":pass_time_in_day} )

    def process_vehicle( self, day_start_end, route_id, vehicle_id, route_coords ):
        #print( "process_vehicle", day_start_end, route_id, vehicle_id )

        curr = self.conn.cursor()
        curr.execute( """select time, lat, lng, dir from vehicle_pos
                            where ? <= time and time < ? and rt_id = ? and vh_id = ?
                            order by time""", day_start_end + ( route_id, vehicle_id ) )
        
        previous_p = None
        previous_t = None
        for row in curr:
            vehicle_pos = { "lat":row[1], "lng":row[2], "direction":row[3] }
            current_p = eway.find_closest_route_point( route_coords, vehicle_pos )
            current_t = row[0]
            if previous_p is not None:
                if ( current_t-previous_t > OFFROUTE_TIME or current_p["index"]<previous_p["index"] and
                     current_p["index"] + route_coords[-1]["index"] - previous_p["index"] > RESTART_LIMIT ):
                    if previous_p is not None and previous_p["is_stop"]:
                        ewaystat.add_vehicle_pass( route_coords[previous_p["index"]], vehicle_id, previous_t )
                    previous_p = None
                    previous_t = None
                else:
                    if previous_p["index"] <= current_p["index"]:
                        for i in range( previous_p["index"], current_p["index"] ):
                            if route_coords[i]["is_stop"]:
                                if current_p["dist_from_start"] == previous_p["dist_from_start"]:
                                    pass_time = previous_t
                                else:
                                    pass_time = ( previous_t + 
                                                (current_t-previous_t) * 
                                                ( ( route_coords[i]["dist_from_start"]-previous_p["dist_from_start"] ) / 
                                                    ( current_p["dist_from_start"]-previous_p["dist_from_start"] ) )
                                                )
                                    #print( "calc_time_stamp", """{} = {} + ({}-{}) * ( ( {}-{} ) / ( {}-{} ) )""".format(
                                    #    pass_time, previous_t, current_t, previous_t, route_coords[i]["dist_from_start"], previous_p["dist_from_start"],
                                    #    current_p["dist_from_start"], previous_p["dist_from_start"]
                                    #) )
                                ewaystat.add_vehicle_pass( route_coords[i], vehicle_id, pass_time )

                    else:
                        dist_zero = route_coords[-1]["dist_from_start"] - previous_p["dist_from_start"]
                        if dist_zero + current_p["dist_from_start"] == 0:
                            time_zero = previous_t
                        else:
                            time_zero = previous_t + (current_t-previous_t) * dist_zero / ( dist_zero + current_p["dist_from_start"] )

                        for i in range( previous_p["index"], route_coords[-1]["index"]+1):
                            if route_coords[i]["is_stop"]:
                                if dist_zero == 0:
                                    pass_time = previous_t
                                else:
                                    pass_time = ( previous_t + 
                                                (time_zero-previous_t) * 
                                                ( ( route_coords[i]["dist_from_start"]-previous_p["dist_from_start"] ) / 
                                                    dist_zero
                                                ) )
                                ewaystat.add_vehicle_pass( route_coords[i], vehicle_id, pass_time )
                        for i in range( current_p["index"] ):
                            if route_coords[i]["is_stop"]:
                                if current_p["dist_from_start"] == 0:
                                    pass_time = time_zero
                                else:
                                    pass_time = ( time_zero + 
                                                (current_t-time_zero) * 
                                                ( route_coords[i]["dist_from_start"] / current_p["dist_from_start"] )
                                                )
                                ewaystat.add_vehicle_pass( route_coords[i], vehicle_id, pass_time )


            previous_p = current_p
            previous_t = current_t
        
        if previous_p is not None and previous_p["is_stop"]:
            ewaystat.add_vehicle_pass( route_coords[previous_p["index"]], vehicle_id, previous_t )

    def process_route( self, day_start_end, route_id, route_coords ):
        #print( "process_route: {}".format( route_id ) )

        curr = self.conn.cursor()
        curr.execute( """select vh_id from vehicle_pos 
                            where ? <= time and time < ? and rt_id = ? 
                            group by vh_id""", day_start_end + (route_id,) )
        for row in curr.fetchall():
            self.process_vehicle( day_start_end, route_id, row[0], route_coords )

    def process_day( self, day_start_end ):
        print( "process_day:", day_start_end )
        curr = self.conn.cursor()
        curr.execute( """select rt_id from vehicle_pos 
                            where ? <= time and time < ? 
                            group by rt_id""", 
                      day_start_end )
        
        for row in curr.fetchall():
            self.process_route( day_start_end, row[0] )

    def process( self ):
        curr = self.conn.cursor()
        earliest, latest = curr.execute( "select min(time), max(time) from vehicle_pos" ).fetchone()
        print( "earliest, latest timestamps are: {}, {}".format( earliest, latest ) )

        curtime = earliest
        while True:
            day_start_end = get_day( curtime )
            self.process_day( day_start_end )
            curtime = day_start_end[1]+1
            if latest < curtime:
                break

def self_test():
    print( "some self-testing before it all begins..." )

    get_day_input = ( 1456578000, 1456581540, 1456616940, 1456620480, 1456624020, 1456627560, 1456662960, 
                      1456701900, 1456705440, 1456708980, 1456712520, 1456747920, 1458824400, 1458827940, 
                      1458863340, 1458866880, 1458870420, 1458873960, 1458912900, 1458948300, 1458951840, 
                      1458955380, 1458958920, 1458990780, 1458994320, )
    get_day_expected = [ (1456534800.0, 1456621200.0 ), (1456534800.0, 1456621200.0 ), (1456534800.0, 1456621200.0 ), 
                         (1456534800.0, 1456621200.0 ), (1456621200.0, 1456707600.0 ), (1456621200.0, 1456707600.0 ), 
                         (1456621200.0, 1456707600.0 ), (1456621200.0, 1456707600.0 ), (1456621200.0, 1456707600.0 ), 
                         (1456707600.0, 1456794000.0 ), (1456707600.0, 1456794000.0 ), (1456707600.0, 1456794000.0 ), 
                         (1458781200.0, 1458867600.0 ), (1458781200.0, 1458867600.0 ), (1458781200.0, 1458867600.0 ), 
                         (1458781200.0, 1458867600.0 ), (1458867600.0, 1458954000.0 ), (1458867600.0, 1458954000.0 ), 
                         (1458867600.0, 1458954000.0 ), (1458867600.0, 1458954000.0 ), (1458867600.0, 1458954000.0 ), 
                         (1458954000.0, 1459040400.0 ), (1458954000.0, 1459040400.0 ), (1458954000.0, 1459040400.0 ), 
                         (1458954000.0, 1459040400.0 ), ]
    if list( map( get_day, get_day_input ) ) == get_day_expected:
        print( "passed: get_day()" )
    else:
        print( "FAILED: get_day()" )

    test_route_coords = [
        {'index': 0, 'direction': 1, 'lat': 49.000, 'lng': 24.000, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop1'}, 
        {'index': 0, 'direction': 1, 'lat': 49.002, 'lng': 24.000, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.004, 'lng': 24.000, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop2'}, 
        {'index': 0, 'direction': 1, 'lat': 49.006, 'lng': 24.001, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.008, 'lng': 24.002, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.010, 'lng': 24.002, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop3'}, 
        {'index': 0, 'direction': 1, 'lat': 49.011, 'lng': 24.004, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.011, 'lng': 24.005, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop4'}, 
        {'index': 0, 'direction': 1, 'lat': 49.010, 'lng': 24.005, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.010, 'lng': 24.007, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.010, 'lng': 24.009, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop5'}, 
        {'index': 0, 'direction': 1, 'lat': 49.009, 'lng': 24.010, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.009, 'lng': 24.012, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.009, 'lng': 24.013, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop6'}, 
        {'index': 0, 'direction': 1, 'lat': 49.009, 'lng': 24.016, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.008, 'lng': 24.016, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.007, 'lng': 24.017, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop7'}, 
        {'index': 0, 'direction': 1, 'lat': 49.007, 'lng': 24.019, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.006, 'lng': 24.019, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.005, 'lng': 24.019, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.005, 'lng': 24.018, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop8'}, 
        {'index': 0, 'direction': 1, 'lat': 49.003, 'lng': 24.018, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.001, 'lng': 24.019, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop9'}, 
        {'index': 0, 'direction': 1, 'lat': 49.000, 'lng': 24.019, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 48.999, 'lng': 24.019, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 48.997, 'lng': 24.020, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop10'}, 
        {'index': 0, 'direction': 1, 'lat': 48.997, 'lng': 24.021, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 48.999, 'lng': 24.021, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.001, 'lng': 24.021, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop11'}, 
        {'index': 0, 'direction': 1, 'lat': 49.003, 'lng': 24.023, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.004, 'lng': 24.023, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop12'}, 
        {'index': 0, 'direction': 1, 'lat': 49.006, 'lng': 24.022, 'dist_from_start': 0, 'is_stop': False }, 
        {'index': 0, 'direction': 1, 'lat': 49.008, 'lng': 24.022, 'dist_from_start': 0, 'is_stop': False }, 

        {'index': 0, 'direction': 2, 'lat': 49.010, 'lng': 24.023, 'dist_from_start': 0, 'is_stop': True, 'title': 'stop13'}, 

        {'lng': 24.022, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.008, 'is_stop': False},
        {'lng': 24.022, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.006, 'is_stop': False},
        {'lng': 24.023, 'direction': 2, 'index': 0, 'title': 'stop14', 'dist_from_start': 0, 'lat': 49.004, 'is_stop': True},
        {'lng': 24.023, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.003, 'is_stop': False},
        {'lng': 24.021, 'direction': 2, 'index': 0, 'title': 'stop15', 'dist_from_start': 0, 'lat': 49.001, 'is_stop': True},
        {'lng': 24.021, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 48.999, 'is_stop': False},
        {'lng': 24.021, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 48.997, 'is_stop': False},
        {'lng': 24.02, 'direction': 2, 'index': 0, 'title': 'stop16', 'dist_from_start': 0, 'lat': 48.997, 'is_stop': True},
        {'lng': 24.019, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 48.999, 'is_stop': False},
        {'lng': 24.019, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.0, 'is_stop': False},
        {'lng': 24.019, 'direction': 2, 'index': 0, 'title': 'stop17', 'dist_from_start': 0, 'lat': 49.001, 'is_stop': True},
        {'lng': 24.018, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.003, 'is_stop': False},
        {'lng': 24.018, 'direction': 2, 'index': 0, 'title': 'stop18', 'dist_from_start': 0, 'lat': 49.005, 'is_stop': True},
        {'lng': 24.016, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.005, 'is_stop': False},
        {'lng': 24.015, 'direction': 2, 'index': 0, 'title': 'stop19', 'dist_from_start': 0, 'lat': 49.006, 'is_stop': True},
        {'lng': 24.015, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.008, 'is_stop': False},
        {'lng': 24.013, 'direction': 2, 'index': 0, 'title': 'stop20', 'dist_from_start': 0, 'lat': 49.009, 'is_stop': True},
        {'lng': 24.012, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.009, 'is_stop': False},
        {'lng': 24.01, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.009, 'is_stop': False},
        {'lng': 24.009, 'direction': 2, 'index': 0, 'title': 'stop21', 'dist_from_start': 0, 'lat': 49.01, 'is_stop': True},
        {'lng': 24.007, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.01, 'is_stop': False},
        {'lng': 24.005, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.01, 'is_stop': False},
        {'lng': 24.005, 'direction': 2, 'index': 0, 'title': 'stop22', 'dist_from_start': 0, 'lat': 49.011, 'is_stop': True},
        {'lng': 24.004, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.011, 'is_stop': False},
        {'lng': 24.002, 'direction': 2, 'index': 0, 'title': 'stop23', 'dist_from_start': 0, 'lat': 49.01, 'is_stop': True},
        {'lng': 24.002, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.008, 'is_stop': False},
        {'lng': 24.001, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.006, 'is_stop': False},
        {'lng': 24.0, 'direction': 2, 'index': 0, 'title': 'stop24', 'dist_from_start': 0, 'lat': 49.004, 'is_stop': True},
        {'lng': 24.0, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.002, 'is_stop': False},
        {'lng': 24.0, 'direction': 2, 'index': 0, 'dist_from_start': 0, 'lat': 49.000, 'is_stop': False},
    ]

    def enum_and_measure_route( coords ):
        from geopy.distance import vincenty
        dist = 0
        for i, p in enumerate( coords ):
            if i>0:
                p["index"] = i
                dist += vincenty( ( coords[i-1]["lat"], coords[i-1]["lng"] ), ( p["lat"], p["lng"] ) ).m
                p["dist_from_start"] = dist
    
    enum_and_measure_route( test_route_coords )

    e = ewaystat()
    e.conn = sqlite3.connect( "data/unittestdata.db" )
    e.process_route( (0, 10000), 1, test_route_coords )
    #for p in ( p for p in test_route_coords if "vehicle_passes" in p ):
    #    print( "vehicle_passes", p["index"], p["title"], p["vehicle_passes"] )
    
    expected_vehicle_passes = [
        ( 0, "stop1", [{'vehicle_id': 1, 'time': 7201}, {'time': 9214, 'vehicle_id': 1}, {'vehicle_id': 1, 'time': 9730}, {'vehicle_id': 1, 'time': 9923}] ), 
        ( 2, "stop2", [{'vehicle_id': 1, 'time': 7259}, {'time': 9220, 'vehicle_id': 1}, {'vehicle_id': 1, 'time': 9930}] ),
        ( 5, "stop3", [{'vehicle_id': 1, 'time': 7332}, {'time': 9230, 'vehicle_id': 1}] ),
        ( 7, "stop4", [{'time': 7352, 'vehicle_id': 1}] ), 
        ( 10, "stop5", [{'time': 7388, 'vehicle_id': 1}] ),
        ( 13, "stop6", [{'vehicle_id': 1, 'time': 7461}] ), 
        ( 16, "stop7", [{'vehicle_id': 1, 'time': 7473}, {'time': 7520, 'vehicle_id': 1}] ), 
        ( 20, "stop8", [{'vehicle_id': 1, 'time': 7484}, {'time': 7640, 'vehicle_id': 1}] ), 
        ( 22, "stop9", [{'vehicle_id': 1, 'time': 7700}] ),
        ( 25, "stop10", [{"vehicle_id":1, "time": 7790}] ),
        ( 28, "stop11", [{"vehicle_id":1, "time": 7880}] ),
        ( 30, "stop12", [{'vehicle_id': 1, 'time': 7911}] ),
        ( 33, "stop13", [{'vehicle_id': 1, 'time': 7922}] ), 
        ( 36, "stop14", [{'vehicle_id': 1, 'time': 7933}] ),
        ( 38, "stop15", [{'vehicle_id': 1, 'time': 7940}] ),
        ( 44, "stop17", [{'vehicle_id': 1, 'time': 8050}] ),
        ( 46, "stop18", [{'time': 8073, 'vehicle_id': 1}] ),
        ( 48, "stop19", [{'time': 8088, 'vehicle_id': 1}] ),
        ( 50, "stop20", [{'time': 8109, 'vehicle_id': 1}] ),
        ( 53, "stop21", [{'vehicle_id': 1, 'time': 8230}] ), 
        ( 56, "stop22", [{'vehicle_id': 1, 'time': 9901}] ), 
        ( 58, "stop23", [{'vehicle_id': 1, 'time': 9200}, {'vehicle_id': 1, 'time': 9905}] ),
        ( 61, "stop24", [{'time': 9209, 'vehicle_id': 1}, {'vehicle_id': 1, 'time': 9916}] ),
    ]

    if expected_vehicle_passes == [ ( s["index"], s["title"], s["vehicle_passes"] ) 
                                    for s in test_route_coords if "vehicle_passes" in s ]:
        print( "passed: process_route()" )
    else:
        print( "FAILED: process_route()" )


def main():
    self_test()

    #e = ewaystat()
    #e.process()

    #route = 11
    #route_coords = eway.get_route_coords( route )
    #e.process_route( (1517274000.0, 1517360400.0), route, route_coords )

    #for stop in ( point for point in route_coords if point["is_stop"] ):
    #    print( stop["title"], stop["vehicle_passes"] if "vehicle_passes" in stop else "", "\n" )

if __name__ == "__main__":
    main()
