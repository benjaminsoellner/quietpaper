import datetime
import dateutil.parser
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from PIL import ImageFont

QP_CALENDAR_FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 12)

class CalendarWidget:

    def __init__(self, auth_file, calendar_id, x, y):
        self.x = x
        self.y = y
        self.data = None
        self.events = []
        self.auth_file = auth_file
        self.calendar_id = calendar_id
        self.service = None
        
    def initialize(self):
        pass

    def retrieve(self, cycle):
        scope = ['https://www.googleapis.com/auth/calendar.readonly']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.auth_file, scope)
        service = build('calendar', 'v3', credentials=credentials)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        self.data = service.events().list(calendarId=self.calendar_id, timeMin=now,
                                                maxResults=10, singleEvents=True, orderBy='startTime').execute()
        self.events = []
        for item in self.data.get('items', []):
            start = item['start'].get('dateTime', item['start'].get('date'))
            self.events.append((dateutil.parser.parse(start), item['summary']))
        
    def get_retrieve_rate(self, cycle):
        return 15
    
    def get_render_rate(self, cycle):
        return 1

    def render(self, display, cycle):
        x = self.x
        y = self.y
        display.erase(x, y, x+326, y+32)
        if len(self.events) > 0:
            now = datetime.datetime.now()
            display.bmp(x, y, "icons/calendar.gif")
            start, text = self.events[0]
            shortened = text[:18]+"..." if len(text)>20 else text
            time = start.strftime("%H:%M")
            day = start.day
            is_today = (start.day == now.day and start.month == now.month and start.year == now.year)
            display.text(x+4+(0 if day < 10 else 3), y+10, str(day), is_red=is_today, font=QP_CALENDAR_FONT)
            display.text(x+46, y+7, time+" "+shortened)


