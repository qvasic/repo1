from my_shift_db import my_shift_db

class my_shift:
    def __init__( self ):
        self.db = my_shift_db()

    def print_all_users( self ):
        print( "all registered users:", *self.db.get_all_users(), sep="\n", end="" )

    def format_HH_MM_SS( t, seconds=False ):
        if t is None:
            return "-"

        import time
        s = time.localtime( t )
        return ( "{:02}:{:02}:{:02}".format( s[3], s[4], s[5] ) 
                 if seconds else
                 "{:02}:{:02}".format( s[3], s[4] ) )

    def format_dur_HH_MM_SS( dur, seconds=False ):
        dur = int( dur )
        SS = dur % 60
        MM = ( dur // 60 ) % 60
        HH = dur // 3600
        return ( "{:02}:{:02}:{:02}".format( HH, MM, SS ) 
                 if seconds else
                 "{:02}:{:02}".format( HH, MM ) )
    
    def menu_print_today( self ):
        import time

        total_worked = 0
        today_start = my_shift_db.get_today_start()

        print( "today" )
        print( "in\tout\tworked" )
        for seg in self.db.get_day_in_out_segments( self.id, time.time() ):
            print( "{}\t{}\t{}".format( my_shift.format_HH_MM_SS( seg[0] ), 
                                        my_shift.format_HH_MM_SS( seg[1] ), 
                                        my_shift.format_dur_HH_MM_SS( seg[2] ) ) )
            total_worked += seg[2]
        print( "total worked: \t{}".format( my_shift.format_dur_HH_MM_SS( total_worked ) ) )

    def menu_print_week( self ):
        import time

        print( "week\nday\tworked" )
        days = [ "mon", "tue", "wed", "thu", "fri", "sat", "sun" ]

        for i, worked in enumerate( self.db.get_week_worked( self.id, time.time() ) ):
            print( "{}\t{}".format( days[i], my_shift.format_dur_HH_MM_SS( worked ) ) )

    def menu_clock_in_out( self ):
        print( "clock_in_out" )
        self.db.clock_in_out( self.id )

    def menu_print_help( self ):
        print( """possible commands
command   explanation
day       print today's clock data (or just press enter)
week      print this week stats
clock     clock in or out
help      print this help
exit      exit""" )

    def menu_toggle_exit( self ):
        self.exit = True

    def run_main_menu( self ):
        self.exit = False
        menu_items = { "":      self.menu_print_today, 
                       "day":   self.menu_print_today, 
                       "week":  self.menu_print_week, 
                       "clock": self.menu_clock_in_out, 
                       "help":  self.menu_print_help, 
                       "exit":  self.menu_toggle_exit
                     }
        while not self.exit:
            cmd = input( "enter command: " )
            if cmd not in menu_items:
                print( "wrong command" )
                self.menu_print_help()
            else:
                menu_items[cmd]()

    def main( self ):
        import sys
        
        if len( sys.argv ) == 1:
            self.print_all_users()
        elif len( sys.argv ) == 2:
            self.id = self.db.get_user_id( sys.argv[1] )
            if self.id is None:
                print( "not user {} exist, create new one".format( sys.argv[1] ) )
                self.id = self.db.create_user( sys.argv[1] )
            print( "using user", sys.argv[1], "with id", self.id )
            self.run_main_menu()
        else:
            print( """wrong parameters
usage:
    {0} - print all users
    {0} <user> - run program for specific user
""".format( sys.argv[0] ) )

if __name__ == "__main__":
    main_object = my_shift()
    main_object.main()
