username = "qvasic"
password = "k3Njd93jdUUSoe2n"
basic_request = "https://api.eway.in.ua/?login={}&password={}&city=lviv".format( username, password )

class EwayRuntimeError(RuntimeError):
    pass

def get_lviv_routes():
    """ retrives all public transpo routes in Lviv from EASY WAY service
        and returns it in form of dict, where keys are route id number
        and value is another dict, with following data for each route:
        "id" - route id number
        "title" - string with name of the route, like "46" or "7H"
        "has_gps" - bool value, whether vehicles on the route have GPS trackers
        "start_position", "stop_position" - index of the first and last point of the route - for routes.GetRouteToDisplay function
        "transport" - type of vehicles on the route, like "bus", or "tram", or else
    """

    import requests
    resp = requests.get( basic_request + "&function=cities.GetRoutesList" )
    if resp.status_code != 200:
        raise EwayRuntimeError( "response from eway server is not ok: {}".format( resp.status_code ) )
    else:
        def convert_route_attribs( route ):
            return { "id":int(route["id"]), 
                     "title":route["title"], 
                     "has_gps":bool(route["has_gps"]), 
                     "start_position":int(route["start_position"]), 
                     "stop_position":int(route["stop_position"]), 
                     "transport":route["transport"] }
        try:
            return { int(route["id"]) : convert_route_attribs( route )
                    for route in resp.json()["routesList"]["route"] }
        except KeyError:
            raise EwayRuntimeError( "caught KeyError: some data is missing, eway service response format has changed?" )

def get_route_coords( id ):
    """ retrieves route coordinates from EASY WAY service
        returns it in for of list of dicts for each point on the route
        each dict has following data:
        "index" - point number from the begining, 
        "lat", "lng" - lattitude and longtitude
        "direction" - number 1 or 2 for "there" or "back"
        "dist_from_start" - meters from the start of the route
        "is_stop" - whether this point is a stop
        "title" - present only if "is_stop" is True, name of the stop
    """

    import requests
    from geopy.distance import vincenty
    route_data = get_lviv_routes()[id]
    start, stop = route_data["start_position"], route_data["stop_position"]
    add_request_params = "&function=routes.GetRouteToDisplay&id={}&start_position={}&stop_position={}".format( id, start, stop )

    coords_resp = requests.get( basic_request + add_request_params )
    if coords_resp.status_code != 200:
        raise EwayRuntimeError( "response from eway server is not ok: {}".format( coords_resp.status_code ) )
    try:
        coords_data = coords_resp.json()["route"]["points"]["point"]
    except KeyError:
        raise EwayRuntimeError( "caught KeyError: some data is missing, eway service response format has changed?" )

    def convert_point_attribs( point, index, dist_from_start ):
        point["index"] = index
        if point["@attributes"]["is_stop"] not in ( "true", "false" ):
            raise ValueError( "is_stop attribute is neither true nor false" )
        point["is_stop"] = True if point["@attributes"]["is_stop"] == "true" else False
        del point["@attributes"]
        point["dist_from_start"] = dist_from_start
        point["lat"] = float( point["lat"] )
        point["lng"] = float( point["lng"] )

    i = iter( coords_data )
    try:
        first = next( i )
        convert_point_attribs( first, 0, 0 )
        prev = first
    except StopIteration:
        pass
    else:
        for n, p in enumerate( i ):
            dist = prev["dist_from_start"] + vincenty( ( prev["lat"], prev["lng"] ),
                                                       ( float( p["lat"] ), float( p["lng"] ) ) ).m
            convert_point_attribs( p, n+1, dist )
            prev = p

    return coords_data

def get_route_vehicles( id ):
    """ retrieves from EASY WAY service current geographic coordinates of all vehicles on a route
        returns data in form of list of dicts for each vehicle
        each dict has following data:
        "id" - id number of vehicle
        "lat", "lng" - latitude and longtitude of vehicle
        "direction" - direction of its current movement, 1 or 2 for "there" or "back"
        "data_relevance", "wifi", "handicapped" - various additional info
    """
    import requests
    vehicles_resp = requests.get( basic_request + "&function=routes.GetRouteGPS&id={}".format( id ) )

    if vehicles_resp.status_code != 200:
        raise EwayRuntimeError( "response from eway server is not ok: {}".format( vehicles_resp.status_code ) )
    data = vehicles_resp.json()
    try:
        if "vehicle" not in data:
            return []
        else:
            return data["vehicle"]
    except KeyError:
        raise EwayRuntimeError( "caught KeyError: some data is missing, eway service response format has changed? data recieved: {}".format( data ) )

################################################################################


def find_closest_route_point( route_coords, vehicle ):
    from geopy.distance import vincenty

    closest, closest_dist = None, None

    for p in route_coords:
        if p["direction"] == vehicle["direction"]:
            dist = vincenty( ( float(vehicle["lat"]), float(vehicle["lng"]) ), 
                             ( float( p["lat"] ), float( p["lng"] ) ) ).m
            if closest_dist is None or closest_dist > dist:
                closest = p
                closest_dist = dist

    if closest is None:
        raise ValueError( "closest point not found: are there points with the same direction at all?" )
    return closest

def get_vehicle_pos_on_route( route_id, vehicle_id=None ):
    route_coords = get_route_coords( route_id )
    vehicles = get_route_vehicles( route_id )

    seq = vehicles if vehicle_id is None else filter(lambda v: v["id"]==vehicle_id, vehicles)

    return { v["id"]:find_closest_route_point( route_coords, v ) 
                for v in seq }

format_str = "{:8} {:>10} {:>4} {:>10} {:>7.4} {:30.30}"
def print_point( point, vehicle_id="" ):
    import time
    print( format_str.format( time.asctime()[11:19], vehicle_id, point["direction"], 
                            point["index"], round( point["dist_from_start"]/100 )/10, 
                            point["title"] if point["is_stop"] == "true" else "" ) )


def track_vehicle_on_route( route_id, vehicle_id ):
    import time
    from itertools import chain

    prev_index = None
    route_points = get_route_coords( route_id )

    print( format_str.format( "time", "vehicle", "dir", "point#", "dist", "stop title" ) )

    while True:
        try:
            vehicles_on_route = get_vehicle_pos_on_route( route_id, vehicle_id )
        except EwayRuntimeError as e:
            print( "       === eway data unavailable: {} ===".format(e.args) )
            prev_index = None
        else:
            if vehicle_id not in vehicles_on_route:
                print( "       === vehicle {} is not on route ===".format(vehicle_id) )
                prev_index = None
            else:
                point = vehicles_on_route[vehicle_id]
                if prev_index is not None:
                    seq = ( range( prev_index+1, point["index"] ) if prev_index <= point["index"] else 
                            chain( range( prev_index+1, len( route_points ) ), range( point["index"] ) ) )
                    for i in seq:
                        if route_points[i]["is_stop"]:
                            print( format_str.format( "", "", "", "", "", route_points[i]["title"] ) )
                print_point( point, vehicle_id )
                prev_index = point["index"]
        time.sleep( 135 )

if __name__ == "__main__":
    print( "eway" )
