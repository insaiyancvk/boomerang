from tkinter import *
from tkcalendar import Calendar
from datetime import date, datetime
from tktimepicker import AnalogPicker, AnalogThemes

def all_children (window) :
    _list = window.winfo_children()

    for item in _list :
        if item.winfo_children() :
            _list.extend(item.winfo_children())

    return _list

def picker():

    root = Tk()
    root.attributes('-topmost',1)

    d = date.today()
    
    # Set geometry
    root.geometry("270x700")
    
    # Add Calendar
    cal = Calendar(
                root, 
                mindate = date.today(),
                background = 'Black',
                selectmode = 'day',
                firstweekday = 'sunday',
                selectbackground = 'Black',
                selectforeground = "White",
                weekendbackground = 'Red',
                weekendforeground = 'White',
                showweeknumbers = False,
                normalbackground = 'White',
                normalforeground = 'Black',
                othermonthforeground = 'Black',
                othermonthbackground = "White",
                othermonthweforeground = '#949494',
                othermonthwebackground = '#EBECF0',
                date_pattern = 'd/m/y',
                year = d.year,
                month = d.month,
                day = d.day)
    

    cal.pack(pady = 20)

    time_picker = AnalogPicker(root)
    time_picker.pack(expand = True, fill="both")

    theme = AnalogThemes(time_picker)
    theme.setNavyBlue()

    Button(
        root, 
        text = "Done",
        command = root.destroy).pack(pady = 20)

    ldate = Label(root, text = "")
    ldate.pack(pady = 5)
    timelbl = Label(root, text = "")
    timelbl.pack(pady = 5)

    root.mainloop()
    
    return [int(i) if i.isdigit() else str(i) for i in cal.get_date().split('/')], list(time_picker.time())

def formatted_datetime():

    sdate, stime = picker()
    # goal - YYYY-MM-DDTHH:MM ✅

    t = str(stime[0])+":"+str(stime[1])+" "+stime[2] 
    in_time = datetime.strptime(t, "%I:%M %p")
    out_time = datetime.strftime(in_time, "%H:%M")
    return str(sdate[2])+"-"+str(sdate[1])+"-"+str(sdate[0])+"T"+out_time

# DD/MM/YYYY
# sdate, stime = picker()
# split the date string by '/' and convert the applicable strings to integer and leave the rest alone
# sdate = 

# Current time
# def current_time():
#     t = datetime.now().strftime("%H %M %p")
#     t = t.split()
#     return [int(i) if i.isdigit() else str(i) for i in t]   # [int, int, str] - [hh, mm, AM/PM]
    
# Compare selected time with current time
# print(stime, current_time(), stime == current_time())

# Current date
# def current_date():
#     dat = date()
#     return [dat.day, dat.month, dat.year]   # [int, int, int] - [dd, mm, yyyy] # TO BE USED: YYYY-MM-DD #
# today = [d.day, d.month, d.year]
# Compare selected date with current date  
# print(today, sdate, sdate == today)