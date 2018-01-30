""" Vehicle position retriver
    Gets data from EASY WAY service about vehicle position on route,
    and stores it in sqlite3 database data/eway.db.
"""

database_path = "data/eway.db"
#          tram 1, tram 9, bus 46, bus 43
routes = ( 11, 339, 212, 162 )
retr_interval = 29

def main():
    import eway
    import time
    import sqlite3

    conn = sqlite3.connect( database_path )
    cur = conn.cursor()

    while True:
        for route_id in routes:
            vehicles = eway.get_route_vehicles( route_id )
            for v in vehicles:
                cur.execute( """INSERT INTO 
                                    VEHICLE_POS (time, rt_id, vh_id, lat, lng, dir, relev) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                            ( int(time.time()), route_id, v["id"], v["lat"], v["lng"], 
                            v["direction"], v["data_relevance"] ) )
            conn.commit()
            print( "{} - {} vehicle positions for route {} stored".format( time.asctime(), len( vehicles ), route_id ) )
        time.sleep( retr_interval )

if __name__ == "__main__":
    main()
