"""

TODO

choosing user
editing

"""

import tkinter as tk
import tkinter.ttk as ttk
from my_shift import my_shift

class my_shift_wnd (tk.Frame):
    def __init__( self, master=None ):
        from my_shift_db import my_shift_db

        super().__init__(master)
        self.pack()

        self.id = 0
        self.db = my_shift_db()

        self.status_lbl = tk.Label( self )
        self.status_lbl["text"] = "OUT"
        self.status_lbl.pack()

        self.clock_btn = tk.Button( self )
        self.clock_btn["text"] = "clock in/out"
        self.clock_btn["command"] = self.clock_btn_clck
        self.clock_btn.pack()

        self.clock_data = ttk.Label( self )
        self.clock_data["text"] = ""
        self.clock_data.pack()

        self.update_clock_data()

    def update_clock_data( self ):
        import time
        clock_data_text = ""

        clock_data_text += "THIS WEEK\nday\tworked\n"
        days = ( 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun' )
        total_worked = 0
        for i, d in enumerate( self.db.get_week_worked( self.id, time.time() ) ):
            clock_data_text += "{}\t{}\n".format( days[i], my_shift.format_dur_HH_MM_SS( d ) )
            total_worked += d
        clock_data_text += ( "\ntotal: \t{}\n".format( my_shift.format_dur_HH_MM_SS( total_worked ) ) )


        total_worked = 0
        clock_data_text += "\nTODAY\nin\tout\tworked\n"
        for seg in self.db.get_day_in_out_segments( self.id, time.time() ):
            clock_data_text += ( "{}\t{}\t{}\n".format( my_shift.format_HH_MM_SS( seg[0] ), 
                                                        my_shift.format_HH_MM_SS( seg[1] ), 
                                                        my_shift.format_dur_HH_MM_SS( seg[2] ) ) )
            total_worked += seg[2]
        clock_data_text += ( "\ntotal: \t\t{}\n".format( my_shift.format_dur_HH_MM_SS( total_worked ) ) )
        self.clock_data["text"] = clock_data_text

        if seg[1] is None:
            self.clock_btn["text"] = "clock out"
            self.status_lbl["text"] = "IN"
            self.status_lbl["bg"] = "green"
        else:
            self.clock_btn["text"] = "clock in"
            self.status_lbl["text"] = "OUT"
            self.status_lbl["bg"] = "red"

        self.after( 60000, self.update_clock_data )

    def clock_btn_clck( self ):
        self.db.clock_in_out( self.id )
        self.update_clock_data()

def main():
    root = tk.Tk()
    wnd = my_shift_wnd(master = root)
    wnd.mainloop()

if __name__ == "__main__":
    main()
