from Tkinter import *
from tkSimpleDialog import Dialog
from datetime import datetime

class MyDialog(Dialog):
    pass

# -----------------------------------------------------------------------------
# class TimeShiftDialog
#        Custom dialog that prompts for a timeshift value in seconds
# -----------------------------------------------------------------------------        
class TimeShiftDialog(MyDialog):
    def __init__(self, master, init_value):
        self.init_value = str(init_value)
        MyDialog.__init__(self, master)
                
    def body(self, master):
        self.result = None
        
        Label(master, text="Enter shift value in seconds (ex: 500, -300").grid(row=0, column=0)
        
        self.entry_value = Entry(master)
        self.entry_value.insert(0, self.init_value)
        self.entry_value.grid(row=1, column=0)
        
        self.entry_value.select_range(0, END)
        self.entry_value.focus_set()
        
    def apply(self):
        str_shift_val = self.entry_value.get()
        new_shift = int(str_shift_val) if str_shift_val else 0 
        
        print "new time shift:", new_shift
        self.result = new_shift
        
# -----------------------------------------------------------------------------
# class DateTimeDialog
#        Custom dialog that prompts for a date/time value to set an item
# -----------------------------------------------------------------------------
class DateTimeDialog(MyDialog):
    def __init__(self, master, init_dt, overriden=False):
        self.init_dt = init_dt
        self.overriden = overriden
        MyDialog.__init__(self, master)
        
    def body(self, master):
        self.result = None
        
        Label(master, text="Enter date: mm/dd/yyyy").grid(row=0, column=0, columnspan=5)
        
        # experiment using StringVars
        self.sv_month = StringVar()
        entry_month = Entry(master, width=3, textvariable=self.sv_month)
        entry_month.grid(row=1, column=0)
        Label(master, text="/").grid(row=1, column=1)
        self.sv_day = StringVar()
        entry_day   = Entry(master, width=3, textvariable=self.sv_day)
        entry_day.grid(row=1, column=2)
        Label(master, text="/").grid(row=1, column=3)
        self.sv_year = StringVar()
        entry_year  = Entry(master, width=5, textvariable=self.sv_year)
        entry_year.grid(row=1, column=4)
        
        Label(master, text="Enter time in format: hh:mm:ss").grid(row=2, column=0, columnspan=5)

        self.entry_hour  = Entry(master, width=3)
        self.entry_hour.grid(row=3, column=0)
        Label(master, text=":").grid(row=3, column=1)
        self.entry_min   = Entry(master, width=3)
        self.entry_min.grid(row=3, column=2)
        Label(master, text=":").grid(row=3, column=3)
        self.entry_sec   = Entry(master, width=3)
        self.entry_sec.grid(row=3, column=4)
        
        self.sv_month.set(str(self.init_dt.month).zfill(2))
        self.sv_day.set(str(self.init_dt.day).zfill(2))
        self.sv_year.set(str(self.init_dt.year))

        self.entry_hour.insert(0, str(self.init_dt.hour).zfill(2))
        self.entry_min.insert(0, str(self.init_dt.minute).zfill(2))
        self.entry_sec.insert(0, str(self.init_dt.second).zfill(2))
        
        self.bv_clear = BooleanVar()
        chkbox = Checkbutton(master, text="Clear override",
                             state=NORMAL if self.overriden else DISABLED,
                             variable=self.bv_clear)
        chkbox.grid(row=4, column=0, columnspan=5)        

        #self.entry_month.select_range(0, END)
        entry_month.focus_set()

    def apply(self):
        if self.bv_clear.get():
            # a clear was requested
            self.result = "clear"
        
        # otherwise, process values
        dt_input = datetime(month=int(self.sv_month.get()), day=int(self.sv_day.get()),
                            year=int(self.sv_year.get()),
                            hour=int(self.entry_hour.get()), minute=int(self.entry_min.get()),
                            second=int(self.entry_sec.get()))
        if dt_input != self.init_dt:
            self.result = dt_input

