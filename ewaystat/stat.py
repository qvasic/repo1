import time
import sqlite3

def get_day( t ):
    "Returns tuple with first and last seconds of the day, which include time t."

    first = list( time.localtime( t ) )
    first[3:6] = ( 0,0,0 )
    last = list( first )
    last[3:6] = ( 23,59,59 )
    return ( int( time.mktime( time.struct_time( first ) ) ), 
             int( time.mktime( time.struct_time( last  ) ) ) )

class ewaystat:
    def __init__( self ):
        self.conn = sqlite3.connect( "data/eway.db" )

    def process_vehicle( self, day_start_end, route_id, vehicle_id ):
        curr = self.conn.cursor()
        curr.execute( """select * from vehicle_pos
                            where ? <= time and time <= ? and rt_id = ? and vh_id = ?
                            order by time""", day_start_end + ( route_id, vehicle_id ) )
        return curr.fetchall()

    def process_route( self, day_start_end, route_id ):
        print( "route: {}".format( route_id ) )
        curr = self.conn.cursor()
        curr.execute( """select vh_id from vehicle_pos 
                            where ? <= time and time <= ? and rt_id = ? 
                            group by vh_id""", day_start_end + (route_id,) )
        print( "vehicles: ", *( ( row[0], len( self.process_vehicle( day_start_end, route_id, row[0] ) ) ) for row in curr.fetchall() ) )

    def process_day( self, day_start_end ):
        print( "day:", day_start_end )
        curr = self.conn.cursor()
        curr.execute( """select rt_id from vehicle_pos 
                            where ? <= time and time <= ? 
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

def main():
    e = ewaystat()
    e.process()

if __name__ == "__main__":
    main()
