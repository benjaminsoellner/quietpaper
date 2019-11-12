import gspread
import json
import time
import datetime
from dateutil import tz
from oauth2client.service_account import ServiceAccountCredentials
from quietpaper import logger

QP_OFFICE_WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
QP_OFFICE_LOOKBEHIND_HOURS = 2
QP_OFFICE_LOOKAHEAD_DAYS = 7 
QP_OFFICE_SOON_MINUTES_FLAG = 120
QP_OFFICE_SOON_MINUTES_NOFLAG = 30

class OfficeWidget:

    def __init__(self, auth_file, sheet_name, data_cell, bmp_name, x, y):
        self.auth_file = auth_file
        self.sheet_name = sheet_name
        self.data_cell = data_cell
        self.lookbehind_hours = QP_OFFICE_LOOKBEHIND_HOURS
        self.lookahead_days = QP_OFFICE_LOOKAHEAD_DAYS
        self.soon_minutes_flag = QP_OFFICE_SOON_MINUTES_FLAG
        self.soon_minutes_noflag = QP_OFFICE_SOON_MINUTES_NOFLAG
        self.bmp_name = bmp_name
        self.x = x
        self.y = y

    def initialize(self):
        self.is_error = True
        self.ordered_times = []
        self.published = None
        self.flags = {}
    
    def retrieve(self, cycle):
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.auth_file, scope)
            gsheets = gspread.authorize(credentials)
            workbook = gsheets.open(self.sheet_name).get_worksheet(0)
            value = workbook.acell(self.data_cell).value
            if value is None or value == "":
                self.data = None
            else:
                self.data = json.loads(value)
            if self.data is None or "Error" in self.data:
                self.is_error = (self.data is not None and "Error" in self.data)
                self.published = None
                self.ordered_times = None
                self.flags = None
            else:
                self.is_error = False
                self.published = self.data["published"]
                self.ordered_times = []
                self.flags = {}
                for ymd in self.data["day_starts"]:
                    hms = self.data["day_starts"][ymd][0]
                    utc = datetime.datetime.strptime("%s %s" % (ymd, hms), "%Y-%m-%d %H:%M:%S")
                    utc = utc.replace(tzinfo=tz.tzutc())
                    event = utc.astimezone(tz.tzlocal())
                    recently = datetime.datetime.now(tz.tzlocal()) - datetime.timedelta(hours=self.lookbehind_hours)
                    latest = datetime.datetime.now(tz.tzlocal()) + datetime.timedelta(days=self.lookahead_days)
                    if event > recently and event < latest:
                        self.ordered_times.append(event)
                        self.flags[event] = self.data["day_starts"][ymd][1]
                self.ordered_times.sort()
        except Exception as e: 
            logger.warning("Cannot retrieve OfficeWidget: " + (e.message if hasattr(e, 'message') else type(e).__name__))


    def get_text(self):
        if self.is_error:
            return "Fehler!"
        elif self.ordered_times is None:
            return "Daten?"
        elif len(self.ordered_times) == 0:
            return "Nix"
        else:
            event = self.ordered_times[0]
            now = datetime.datetime.now(tz.tzlocal())
            flag = self.flags[event]
            text = ""
            if event.year != now.year or event.month != now.month or event.day != now.day:
                text += QP_OFFICE_WEEKDAYS[event.weekday()] + " "
            text += event.strftime("%H:%M")
            text += "*" if flag else ""
            return text
            
    def is_soon(self):
        if self.is_error:
            return True
        elif self.ordered_times is None or len(self.ordered_times) == 0: 
            return False
        else:
            event = self.ordered_times[0]
            flag = self.flags[event]
            soon_minutes = self.soon_minutes_flag if flag else self.soon_minutes_noflag
            soon = datetime.datetime.now(tz.tzlocal()) + datetime.timedelta(minutes=soon_minutes)
            return event < soon

    def get_retrieve_rate(self, cycle):
        return 60
    
    def get_render_rate(self, cycle):
        return 1

    def render(self, display, cycle):
        text = self.get_text()
        is_soon = self.is_soon()
        x = self.x
        y = self.y
        display.erase(x, y, x+152, y+32)
        display.text(x+46, y+7, text, is_red=is_soon)
        display.bmp(x, y, ("icons/office_%s.bmp" % self.bmp_name))
        return True
