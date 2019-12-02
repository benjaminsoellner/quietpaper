import gspread
import json
import time
import datetime
import dateutil.parser
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from dateutil import tz
from oauth2client.service_account import ServiceAccountCredentials
from quietpaper import logger

QP_OFFICE_WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
QP_OFFICE_LOOKBEHIND_HOURS = 2
QP_OFFICE_LOOKAHEAD_DAYS = 7 
QP_OFFICE_SOON_MINUTES_FLAG = 120
QP_OFFICE_SOON_MINUTES_NOFLAG = 30

class GcalOfficeStrategy:

    def __init__(self, auth_file, calender_id):
        self.auth_file = auth_file
        self.calender_id = calender_id
    
    def initialize(self, office_widget):
        office_widget.ordered_times = []
        office_widget.flags = {}
        office_widget.is_error = True
        office_widget.published = None

    def retrieve(self, office_widget, cycle):
        scope = ['https://www.googleapis.com/auth/calendar.readonly']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.auth_file, scope)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        try:
            service = build('calendar', 'v3', credentials=credentials)
            data = service.events().list(calendarId=self.calender_id, timeMin=now,
                                                    maxResults=20, singleEvents=True, orderBy='startTime').execute()
            day = datetime.datetime.now()
            office_widget.ordered_times = []
            office_widget.flags = {}
            office_widget.is_error = False
            office_widget.published = None
            for item in data.get('items', []):
                item_datetime = dateutil.parser.parse(item['start'].get('dateTime', item['start'].get('date'))).replace(tzinfo=tz.tzlocal())
                if item_datetime.date() >= day.date():
                    office_widget.ordered_times.append(item_datetime)
                    office_widget.flags[item_datetime] = False
                    day = item_datetime + datetime.timedelta(hours=24)
        except Exception as e:
            logger.warning("Cannot retrieve GcalOfficeStrategy: " +  (e.message if hasattr(e, 'message') else type(e).__name__))


class GsheetsOfficeStrategy:

    def __init__(self, auth_file, sheet_name, data_cell):
        self.auth_file = auth_file
        self.sheet_name = sheet_name
        self.data_cell = data_cell
        self.lookbehind_hours = QP_OFFICE_LOOKBEHIND_HOURS
        self.lookahead_days = QP_OFFICE_LOOKAHEAD_DAYS

    def initialize(self, office_widget):
        office_widget.is_error = True
        office_widget.ordered_times = []
        office_widget.published = None
        office_widget.flags = {}
    
    def retrieve(self, office_widget, cycle):
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
                office_widget.is_error = (self.data is not None and "Error" in self.data)
                self.published = None
                office_widget.ordered_times = None
                office_widget.flags = None
            else:
                office_widget.is_error = False
                office_widget.published = datetime.datetime.strptime(self.data["published"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz.tzutc())
                office_widget.ordered_times = []
                office_widget.flags = {}
                for ymd in self.data["day_starts"]:
                    hms = self.data["day_starts"][ymd][0]
                    utc = datetime.datetime.strptime("%s %s" % (ymd, hms), "%Y-%m-%d %H:%M:%S")
                    utc = utc.replace(tzinfo=tz.tzutc())
                    event = utc.astimezone(tz.tzlocal())
                    recently = datetime.datetime.now(tz.tzlocal()) - datetime.timedelta(hours=self.lookbehind_hours)
                    latest = datetime.datetime.now(tz.tzlocal()) + datetime.timedelta(days=self.lookahead_days)
                    if event > recently and event < latest:
                        office_widget.ordered_times.append(event)
                        office_widget.flags[event] = self.data["day_starts"][ymd][1]
                office_widget.ordered_times.sort()
        except Exception as e: 
            logger.warning("Cannot retrieve GsheetsOfficeWidget: " + (e.message if hasattr(e, 'message') else type(e).__name__))


class OfficeWidget:

    def __init__(self, office_strategy, bmp_name, x, y):
        self.office_strategy = office_strategy
        self.soon_minutes_flag = QP_OFFICE_SOON_MINUTES_FLAG
        self.soon_minutes_noflag = QP_OFFICE_SOON_MINUTES_NOFLAG
        self.bmp_name = bmp_name
        self.x = x
        self.y = y

    def initialize(self):
        self.office_strategy.initialize(self)
    
    def retrieve(self, cycle):
        self.office_strategy.retrieve(self, cycle)

    def get_retrieve_rate(self, cycle):
        return 30
    
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
            is_outdated = self.published is not None and (now - self.published > datetime.timedelta(days=2))
            text = ""
            if event.year != now.year or event.month != now.month or event.day != now.day:
                text += QP_OFFICE_WEEKDAYS[event.weekday()] + " "
            text += event.strftime("%H:%M")
            text += "*" if flag else ""
            text += "?" if is_outdated else ""
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