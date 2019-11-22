import datetime
import json

def load_dates(dates):
    now = datetime.datetime.now() 
    result = []
    for date in dates:
        time = datetime.datetime.strptime(date + " 12:00", "%Y-%m-%d %H:%M")
        if time > now: 
            result.append(time + datetime.timedelta(hours=12))
    return result

def render_icon(display, x, y, bmp, dates):
    now = datetime.datetime.now() 
    if len(dates) > 0:
        date = dates[0]
        is_soon = (date-now < datetime.timedelta(hours=48))
        is_today = (date-now < datetime.timedelta(hours=24))
        if is_soon:
            display.bmp(x, y, bmp, is_red=is_today)
        return is_soon
    else:
        return False

class TrashdayWidget:

    def __init__(self, trashday_file, x, y):
        self.trashday_file = trashday_file
        self.x = x
        self.y = y
        self.data = None
        self.dates = []

    def initialize(self):
        pass
        
    def retrieve(self, cycle):
        with open(self.trashday_file, "r") as fd:
            data = json.load(fd)
        self.recycle_dates = load_dates(data["recycle"])
        self.waste_dates = load_dates(data["waste"])
        self.bio_dates = load_dates(data["bio"])
        self.paper_dates = load_dates(data["paper"])
        
    def get_retrieve_rate(self, cycle):
        return 60*24
    
    def get_render_rate(self, cycle):
        return 60
    
    def render(self, display, cycle):
        x = self.x
        y = self.y
        now = datetime.datetime.now() 
        display.erase(x, y, x+68, y+32)
        offset = 0
        offset += 23 if render_icon(display, x+offset, y, "icons/date_trash_recycle.bmp", self.recycle_dates) else 0
        offset += 15 if render_icon(display, x+offset, y, "icons/date_trash_paper.bmp",   self.paper_dates)   else 0
        offset += 15 if render_icon(display, x+offset, y, "icons/date_trash_waste.bmp",   self.waste_dates)   else 0
        offset += 15 if render_icon(display, x+offset, y, "icons/date_trash_bio.bmp",     self.bio_dates)     else 0
        
