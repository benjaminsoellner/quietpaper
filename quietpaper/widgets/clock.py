import datetime

QP_CLOCK_WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
QP_CLOCK_MONTHS = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

class ClockWidget:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.data = False
        self.is_smog = False

    def initialize(self):
        pass
        
    def retrieve(self, cycle):
        pass
        
    def get_retrieve_rate(self, cycle):
        return None
    
    def get_render_rate(self, cycle):
        return 1

    def render(self, display, cycle):
        x = self.x
        y = self.y
        now = datetime.datetime.now()
        text = "%s %02d %s %04d" % (QP_CLOCK_WEEKDAYS[now.weekday()], now.day, QP_CLOCK_MONTHS[now.month-1], now.year)
        if not cycle.is_slow:
            text += " " + now.strftime("%H:%M")
        display.erase(x, y, x+196, y+32)
        display.text(x, y+7, text)