import datetime
import json

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
        now = datetime.datetime.now() 
        with open(self.trashday_file, "r") as fd:
            dates = json.load(fd)
        self.dates = []
        for date in dates:
            time = datetime.datetime.strptime(date, "%Y-%m-%d")
            if time > now - datetime.timedelta(days=1): 
                self.dates.append(time)
        self.dates.sort()
        
    def get_retrieve_rate(self, cycle):
        return 60*24
    
    def get_render_rate(self, cycle):
        return 60

    def render(self, display, cycle):
        x = self.x
        y = self.y
        now = datetime.datetime.now() 
        soon = now + datetime.timedelta(days=3)
        if len(self.dates) > 0:
            display.erase(x, y, x+32, y+32)
            date = self.dates[0]
            if date < soon:
                is_today = (date.day == now.day and date.month == now.month and date.year == now.year)
                display.bmp(x, y, "icons/date_trashday.gif", is_red=is_today)