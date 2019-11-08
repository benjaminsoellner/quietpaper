import os
import math
import json
from quietpaper.iot.tado import TadoConnection
from quietpaper.iot.epd7in5b import EPD_HEIGHT, EPD_WIDTH
from quietpaper.widgets.office import OfficeWidget
from quietpaper.widgets.commute import CommuteWidget
from quietpaper.widgets.room import RoomWidget
from quietpaper.widgets.smog import SmogWidget
from quietpaper.widgets.trashday import TrashdayWidget
from quietpaper.widgets.clock import ClockWidget
from quietpaper.widgets.monitor import MonitorWidget
from quietpaper.widgets.weather import WeatherWidget
from quietpaper.widgets.allergy import AllergyWidget
from quietpaper.widgets.cal import CalendarWidget
from quietpaper.widgets.seperator import Seperator
from quietpaper.screens.mock import MockScreen
from quietpaper.screens.epaper import EpaperScreen
from quietpaper.controller import Controller
from quietpaper.display import Display

with open(os.environ.get("QP_SECRETS_FILE", "secret/_secrets.json"), "r") as fd:
    secrets = json.load(fd)

def secret(key, default=""):
    return os.environ.get(key, secrets.get(key, default))

# Office widget
office_auth_file = secret("QP_OFFICE_AUTH_FILE", "secret/homeprojects-d5131777a160.json")
office_sheet_name = "goodmorning"
office_data_range_benj = "B1"
office_data_range_sara = "B2"
office_bmp_name_benj = "benjamin"
office_bmp_name_sara = "sara"
office_x_sara = 313
office_y_sara = 124
office_x_benj = 465
office_y_benj = 124
office_benj = OfficeWidget(office_auth_file, office_sheet_name, office_data_range_benj, office_bmp_name_benj, office_x_benj, office_y_benj)
office_sara = OfficeWidget(office_auth_file, office_sheet_name, office_data_range_sara, office_bmp_name_sara, office_x_sara, office_y_sara)

# Commute widget
commute_api_key_file = secret("QP_COMMUTE_API_KEY_FILE")
commute_from_loc = "Hans-Rehn-Stift"
commute_to_loc = "Stuttgart-Stadtmitte"
commute_leave_for_bus = 5
commute_leave_for_train = 30
commute_x = 314
commute_y = 228
commute = CommuteWidget(commute_api_key_file, commute_from_loc, commute_to_loc, commute_leave_for_bus, commute_leave_for_train, commute_x, commute_y)

# Tado Connection
tado_client_secrets_file = secret("QP_TADO_CLIENT_SECRETS_FILE")
tado_username = secret("QP_TADO_USERNAME")
tado_password = secret("QP_TADO_PASSWORD")
tado = TadoConnection(tado_client_secrets_file, tado_username, tado_password)

# Room widget
room_y_offset = 0
rooms = []
for (room_name, room_zone) in [("living", 1), ("bed", 2), ("office", 3), ("closet", 4), ("bath", 5), ("twinbath", 6)]:
    room_max_humidity = 60 if room_zone > 4 else 65
    room_x = 22
    room_y = math.ceil(72 + room_y_offset)
    room_y_offset += 51.5
    room = RoomWidget(tado, room_zone, room_max_humidity, room_name, room_x, room_y)
    rooms.append(room)

# Smog widget
smog_x = 584
smog_y = 176
smog = SmogWidget(smog_x, smog_y)

# Clock widget
clock_x = 314
clock_y = 22
clock = ClockWidget(clock_x, clock_y)

# Trashday widget
trashday_file = "data/trashday.json"
trashday_x = 510
trashday_y = 22
trashday = TrashdayWidget(trashday_file, trashday_x, trashday_y)

# Monitor widget
monitor_nas_host = "192.168.178.33"
monitor_vpn_host = "house.benkku.com"
monitor_x = 584
monitor_y = 22
monitor = MonitorWidget(monitor_nas_host, monitor_vpn_host, monitor_x, monitor_y)

# Weather widget
weather_api_key_file = secret("QP_WEATHER_API_KEY_FILE")
weather_zip_location = "70565,de"
weather_x = 23
weather_y = 23
weather = WeatherWidget(weather_api_key_file, weather_zip_location, weather_x, weather_y)

# Allergy widget
allergy_purifier_host = "192.168.178.21"
allergy_x = 314
allergy_y = 176
allergy = AllergyWidget(allergy_purifier_host, allergy_x, allergy_y)

# Calendar widget
calendar_auth_file = secret("QP_CALENDAR_AUTH_FILE")
calendar_id = secret("QP_CALENDAR_ID")
calendar_x = 314
calendar_y = 73
calendar = CalendarWidget(calendar_auth_file, calendar_id, calendar_x, calendar_y)

# Seperator
seperator_x1 = 12
seperator_x2 = 12+616
seperator_y1 = seperator_y2 = 62
seperator = Seperator(seperator_x1, seperator_y1, seperator_x2, seperator_y2)

# MockScreen
mock_debug_bmp = "output.bmp"
mock = MockScreen(mock_debug_bmp)

# EpaperScreen
epaper = EpaperScreen()

# Display 
display_height = EPD_HEIGHT
display_width = EPD_WIDTH
display = Display(display_width, display_height)

# Controller
debug_bmp = 'output.bmp'
controller = Controller(display)
controller.register_widget(office_sara)
controller.register_widget(office_benj)
controller.register_widget(commute)
for room in rooms:
    controller.register_widget(room)
controller.register_widget(smog)
controller.register_widget(clock)
controller.register_widget(trashday)
controller.register_widget(monitor)
controller.register_widget(weather)
controller.register_widget(allergy)
controller.register_widget(seperator)
controller.register_widget(calendar)
controller.register_screen(mock)
controller.register_screen(epaper)