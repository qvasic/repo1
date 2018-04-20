class my_shift_db:
    IN = 0
    OUT = 1
    DATABASE_PATH = "my_shift.db"

    def get_day_start_end( t ):
        """ Returns tuple with day's first second and 
        one past last (in effect - next day's first second).
        Parameter:
        t - any second of the day in question.
        Example: takes t=1521917008, returns (1521842400, 1521928800)
        """
        import time
        first_struct = list( time.localtime( t ) )
        last_struct = list( first_struct )
        first_struct[3:6] = ( 0, 0, 0 )
        last_struct[3:6] = ( 23, 59, 59 )
        return ( int( time.mktime( time.struct_time( first_struct ) ) ), 
                 int( time.mktime( time.struct_time( last_struct ) ) )+1 )

    def get_today_start():
        import time
        return my_shift_db.get_day_start_end( time.time() )[0]

    def __init__( self ):
        import sqlite3
        self.conn = sqlite3.connect( my_shift_db.DATABASE_PATH )
    
    def get_all_users( self ):
        """ Returns list with all users registered in the system. """
        curr = self.conn.cursor()
        curr.execute( "select name from users" )
        return [ row[0] for row in curr ]

    def get_user_id( self, name ):
        curr = self.conn.cursor()
        row  = curr.execute( "select id from users where name = ?", ( name, ) ).fetchone()
        if row is None:
            return None
        else:
            return row[0]

    def create_user( self, name ):
        curr = self.conn.cursor()
        row  = curr.execute( "select max(id) from users" ).fetchone()
        if row is None or row[0] is None:
            newid = 0
        else:
            newid = row[0]+1
        curr.execute( "insert into users (name, id) values (?, ?)", ( name, newid ) )
        self.conn.commit()
        return newid

    def clock_in_out( self, id ):
        import time
        curr = self.conn.cursor()
        last_clock_entry = curr.execute( """select in_out 
                                                from clock_data 
                                                where user_id = ? and time = ( select max(time) from clock_data where user_id = ? )""", 
                                         ( id, id ) ).fetchall()
        if len( last_clock_entry ) == 0:
            dir = my_shift_db.IN
        else:
            dir = my_shift_db.IN if last_clock_entry[-1][0] == my_shift_db.OUT else my_shift_db.OUT
        curr.execute( "insert into clock_data ( user_id, time, in_out ) values ( ?, ?, ? )",
                      ( id, int( time.time() ), dir ) )
        self.conn.commit()

    def get_today_clock_data( self, id ):
        import time
        return self.get_day_clock_data( id, time.time() )

    def get_day_clock_data( self, id, t ):
        """Return all clock_data records for the day, 
           plus one record before that day (if there is any)."""
        curr = self.conn.cursor()
        first, last = my_shift_db.get_day_start_end( t )
        query = """select time, in_out 
                        from clock_data 
                        where user_id = ? and 
                            time >= ifnull( ( select max(time) from clock_data 
                                                  where user_id = ? and time < ? ), ? )
                                and
                            time < ?
                        order by time"""
        curr.execute( query, ( id, id, first, first, last ) )
        return curr.fetchall()

    def get_day_in_out_segments( self, id, t ):
        """Returns list of tuple in form ( clock_in, clock_out, time_worked).
        clock_in of the first record might be None, 
        this means user didn't clocked out the day before.

        clock_out of the last record might be None, this means that user is not clock_out today, 
        or didn't clocked out in the end of the day in question.
        """
        import time
        segs = []
        first, last = my_shift_db.get_day_start_end( t )
        last_clock_in = None
        for r in self.get_day_clock_data( id, t ):
            if r[1] == my_shift_db.IN:
                if last_clock_in is None:
                    last_clock_in = r[0]
            elif last_clock_in is not None:
                if last_clock_in < first:
                    segs.append( ( None, r[0], r[0]-first ) )
                else:
                    segs.append( ( last_clock_in, r[0], r[0]-last_clock_in ) )
                last_clock_in = None

        if last_clock_in is not None:
            effective_last = int( last if last < time.time() else time.time() )
            if last_clock_in < first:
                segs.append( ( None, None, effective_last-first ) )
            else:
                segs.append( ( last_clock_in, None, effective_last-last_clock_in ) )
        return segs

    def get_week_worked( self, id, t ):
        import time

        cur = t
        wday = time.localtime( cur ).tm_wday
        days_worked = []
        for i in range( wday+1 ):
            day_worked = sum( s[2] for s in self.get_day_in_out_segments( id, cur ) )
            days_worked.append( day_worked )
            cur = my_shift_db.get_day_start_end( cur )[0]-1

        return list( reversed( days_worked ) )

    def get_prev_week_worked_total( self, id, t ):
        import time

        cur = t
        wday = time.localtime( cur ).tm_wday
        for i in range( wday+1 ):
            cur = my_shift_db.get_day_start_end( cur )[0]-1
        return sum( self.get_week_worked( id, cur ) )

def run_tests():
    print( "running unit test cases" )

    from unittestcases import run_tests
    my_shift_db.DATABASE_PATH = "my_shift_testdata.db"
    db = my_shift_db()

    unit_test_cases = (
        ( db.get_all_users, [], [ "user1", "user2", "petro", "vova" ] ), 
        ( db.get_user_id, [ "user1" ], 0 ), 
        ( db.get_user_id, [ "user2" ], 1 ), 
        ( db.get_user_id, [ "vova" ], 3 ), 
        ( db.create_user, [ "qvasic" ], 4 ), 
        ( db.get_all_users, [], [ "user1", "user2", "petro", "vova", "qvasic" ] ), 
    )
    run_tests( unit_test_cases )

    curr = db.conn.cursor()
    curr.execute( "delete from users where name = ?", ( "qvasic", ) )
    db.conn.commit()
    del curr

    unit_test_cases = (
        ( db.get_all_users, [], [ "user1", "user2", "petro", "vova" ] ), 
        ( db.get_day_clock_data, [ 0, 79200 ], [(107000, 1), (108000, 0), (111600, 1), (111620, 1), (115200, 0), (115900, 0), (118800, 1), (119800, 1)] ),
        ( db.get_day_in_out_segments, [0, 79200], [(108000, 111600, 3600), (115200, 118800, 3600)] ),

        ( db.get_day_clock_data, [ 0, 165600 ], [(119800, 1), (241200, 0), (244800, 1), (248400, 0)] ),
        ( db.get_day_in_out_segments, [0, 165600], [(241200, 244800, 3600), (248400, None, 3600)] ),

        ( db.get_day_clock_data, [ 0, 165600 ], [(119800, 1), (241200, 0), (244800, 1), (248400, 0)] ),
        ( db.get_day_in_out_segments, [0, 165600], [(241200, 244800, 3600), (248400, None, 3600)] ),

        ( db.get_day_clock_data, [ 0, 252000], [(248400, 0), (255600, 1), (259200, 0), (262800, 1)] ),
        ( db.get_day_in_out_segments, [0, 252000], [(None, 255600, 3600), (259200, 262800, 3600)] ),
    )
    run_tests( unit_test_cases )

    CURRENT_TIME = 423000
    def TIME_TIME_SUBSTITUTE():
        return CURRENT_TIME
    import sys
    TIME_TIME_BACKUP = sys.modules["time"].time
    sys.modules["time"].time = TIME_TIME_SUBSTITUTE

    unit_test_cases = (
        ( db.get_day_clock_data, [ 0, 424799 ], [ (262800, 1), (421200, 0) ] ),
        ( db.get_day_in_out_segments, [0, 424799], [(421200, None, 1800)] ),
    )
    run_tests( unit_test_cases )

    CURRENT_TIME = 423020
    unit_test_cases = (
        ( db.get_day_in_out_segments, [0, 424799], [(421200, None, 1820)] ),
    )
    run_tests( unit_test_cases )

    CURRENT_TIME = 426600
    unit_test_cases = (
        ( db.get_day_in_out_segments, [0, 424799], [(421200, None, 3600)] ),
        ( db.get_day_clock_data, [ 0, 424800 ], [ (421200, 0) ] ),
        ( db.get_day_in_out_segments, [0, 424800], [(None, None, 1800)] ),
    )
    run_tests( unit_test_cases )

    CURRENT_TIME = 426661
    unit_test_cases = (
        ( db.get_day_in_out_segments, [0, 424800], [(None, None, 1861)] ),
    )
    run_tests( unit_test_cases )

    CURRENT_TIME = 513000
    unit_test_cases = (
        ( db.get_day_in_out_segments, [0, 424800], [(None, None, 86400)] ),
        ( db.get_day_in_out_segments, [0, 511200], [(None, None, 1800)] ),
    )
    run_tests( unit_test_cases )

    CURRENT_TIME = 513001
    unit_test_cases = (
        ( db.get_day_in_out_segments, [0, 511200], [(None, None, 1801)] ),
    )
    run_tests( unit_test_cases )

    unit_test_cases = (
        ( db.get_week_worked, [0, 338300 ], [ 0, 0, 0, 0, 7200, 7200, 7200 ] ),
        ( db.get_week_worked, [0, 513001 ], [ 3600, 86400, 1801 ] ),
    )
    run_tests( unit_test_cases )

    sys.modules["time"].time = TIME_TIME_BACKUP

if __name__ == "__main__":
    run_tests()