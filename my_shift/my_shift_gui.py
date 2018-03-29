"""

TODO

weekly
choosing user
editing
misc bugs

testcases

"""

import tkinter as tk
import tkinter.ttk as ttk
from my_shift import my_shift_db, my_shift

class my_shift_wnd (tk.Frame):
    def __init__( self, master=None ):
        super().__init__(master)
        self.pack()

        self.id = 0
        self.db = my_shift_db()

        self.update_btn = tk.Button( self )
        self.update_btn["text"] = "update"
        self.update_btn["command"] = self.update_btn_clck
        self.update_btn.pack()

        self.clock_btn = tk.Button( self )
        self.clock_btn["text"] = "clock in/out"
        self.clock_btn["command"] = self.clock_btn_clck
        self.clock_btn.pack()

        self.clock_data = ttk.Label( self )
        self.clock_data["text"] = ""
        self.clock_data.pack()

        self.update_btn_clck()

    def update_btn_clck( self ):
        import time

        total_worked = 0
        last_clock_in = None
        today_start = my_shift_db.get_today_start()

        clock_data_text = "today\n"
        clock_data_text += "in\tout\tworked\n"
        for l in self.db.get_today_clock_data( self.id ):
            if l[1] == my_shift_db.IN and last_clock_in is None:
                last_clock_in = l[0]
            elif l[1] == my_shift_db.OUT and not last_clock_in is None:
                if last_clock_in < today_start:
                    worked = l[0] - today_start
                    clock_data_text += ( "{}\t{}\t{}\n".format( "", 
                                                my_shift.format_HH_MM_SS( l[0] ), 
                                                my_shift.format_dur_HH_MM_SS( worked ) ) )
                else:
                    worked = l[0] - last_clock_in
                    clock_data_text += ( "{}\t{}\t{}\n".format( my_shift.format_HH_MM_SS( last_clock_in ), 
                                                              my_shift.format_HH_MM_SS( l[0] ), 
                                                              my_shift.format_dur_HH_MM_SS( worked ) ) )
                total_worked += worked
                last_clock_in = None

        if not last_clock_in is None:
            worked = int( time.time() ) - last_clock_in
            clock_data_text += ( "{}\t{}\t{}\n".format( my_shift.format_HH_MM_SS( last_clock_in ), 
                                        "", 
                                        my_shift.format_dur_HH_MM_SS( worked ) ) )
            total_worked += worked
        clock_data_text += ( "\ntotal worked: \t{}\n".format( my_shift.format_dur_HH_MM_SS( total_worked ) ) )

        self.clock_data["text"] = clock_data_text

        self.after( 60000, self.update_btn_clck )

    def clock_btn_clck( self ):
        self.db.clock_in_out( self.id )
        self.update_btn_clck()

def main():
    root = tk.Tk()
    wnd = my_shift_wnd(master = root)
    wnd.mainloop()

if __name__ == "__main__":
    main()
