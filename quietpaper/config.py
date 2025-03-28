import os
import math
import json
from quietpaper.iot.tado import TadoConnection
from quietpaper.iot.meross import MerossConnection
from quietpaper.widgets.office import (
    OfficeWidget,
    GsheetsOfficeStrategy,
    GcalOfficeStrategy
)
from quietpaper.widgets.commute import (
    CommuteWidget,
    DBClientCommuteStrategy
)
from quietpaper.widgets.room import RoomWidget
from quietpaper.widgets.smog import SmogWidget
from quietpaper.widgets.trashday import TrashdayWidget
from quietpaper.widgets.clock import ClockWidget
from quietpaper.widgets.monitor import MonitorWidget
from quietpaper.widgets.weather import WeatherWidget
from quietpaper.widgets.allergy import AllergyWidget
from quietpaper.widgets.cal import CalendarWidget
from quietpaper.widgets.laundry import (
    LaundryMachine,
    LaundryWidget
)
from quietpaper.widgets.seperator import Seperator
from quietpaper.screens.mock import MockScreen
from quietpaper.screens.epaper import EpaperScreen
from quietpaper.screens.gdrive import GdriveScreen
from quietpaper.controller import Controller
from quietpaper.display import Display

with open(os.environ.get("QP_SECRETS_FILE", "secret/_secrets.json"), "r") as fd:
    secrets = json.load(fd)

def secret(key, default=""):
    return os.environ.get(key, secrets.get(key, default))

# Office widget

office_auth_file_guy = office_auth_file_gal = secret("QP_OFFICE_AUTH_FILE")
office_sheet_name_guy = "goodmorning"
office_data_cell_guy = "B1"
office_gsheets_guy = GsheetsOfficeStrategy(office_auth_file_guy, office_sheet_name_guy, office_data_cell_guy)
office_calendar_id_gal = secret("QP_OFFICE_CALENDAR_ID_GAL")
office_gcal_gal = GcalOfficeStrategy(office_auth_file_gal, office_calendar_id_gal)
office_bmp_name_guy = "guy"
office_bmp_name_gal = "gal"
office_x_gal = 313
office_y_gal = 124
office_x_guy = 465
office_y_guy = 124
office_guy = OfficeWidget(office_gsheets_guy, office_bmp_name_guy, office_x_guy, office_y_guy)
office_gal = OfficeWidget(office_gcal_gal, office_bmp_name_gal, office_x_gal, office_y_gal)

# Commute widget
commute_leave_for_bus = 10
commute_leave_for_train = 30
commute_x = 314
commute_y = 228
commute_bus_stations = secret("QP_COMMUTE_BUS_STATIONS")
commute_train_stations = secret("QP_COMMUTE_TRAIN_STATIONS")
commute_dbclient = DBClientCommuteStrategy(commute_bus_stations, commute_train_stations)
commute = CommuteWidget(commute_dbclient, commute_leave_for_bus, commute_leave_for_train, commute_x, commute_y)

# Tado Connection
tado_refresh_token_file = secret("QP_TADO_REFRESH_TOKEN_FILE")
tado = TadoConnection(tado_refresh_token_file)

# Room widget
room_y_offset = 0
rooms = []
for (room_name, room_zone) in [("living", 1), ("bed", 4), ("kid", 2), ("office", 3), ("bath", 5), ("twinbath", 6)]:
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
trashday_x = 500
trashday_y = 22
trashday = TrashdayWidget(trashday_file, trashday_x, trashday_y)

# Monitor widget
monitor_nas_host = secret("QP_MONITOR_NAS_HOST")
monitor_vpn_host = secret("QP_MONITOR_VPN_HOST")
monitor_x = 584
monitor_y = 22
monitor = MonitorWidget(monitor_nas_host, monitor_vpn_host, monitor_x, monitor_y)

# Weather widget
weather_api_key_file = secret("QP_WEATHER_API_KEY_FILE")
weather_zip_location = secret("QP_WEATHER_ZIP_LOCATION")
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

# Laundry
meross_connection = MerossConnection(secret("QP_MEROSS_EMAIL"), secret("QP_MEROSS_PASSWORD"), secret("QP_MEROSS_URL"))
washing_machine = LaundryMachine(
    secret("QP_LAUNDRY_WASHING_MACHINE"),
    meross_connection,
    secret("QP_LAUNDRY_WASHING_STBY_POWER"),
    secret("QP_LAUNDRY_WASHING_ACTIVE_POWER"))
drying_machine = LaundryMachine(
    secret("QP_LAUNDRY_DRYING_MACHINE"),
    meross_connection,
    secret("QP_LAUNDRY_DRYING_STBY_POWER"),
    secret("QP_LAUNDRY_DRYING_ACTIVE_POWER"))
laundry_x = 186
laundry_y = 22
laundry = LaundryWidget(laundry_x, laundry_y, washing_machine, drying_machine, meross_connection)

# MockScreen
mock_png = "output/output.png"
mock = MockScreen(mock_png)
#mock_continuous_png = "output/output_%s.png"
#mock_continuous = MockScreen(mock_continuous_png, add_date=True)

# EpaperScreen
epaper = EpaperScreen(version=3)

# GdriveScreen
gdrive_auth_file = secret("QP_GDRIVE_AUTH_FILE")
gdrive_file_id = secret("QP_GDRIVE_FILE_ID")
gdrive_file_locally = mock_png
gdrive = GdriveScreen(gdrive_auth_file, gdrive_file_id, gdrive_file_locally)

# Display 
display_width = 640
display_height = 384
display = Display(display_width, display_height)

# Controller
controller = Controller(display)
controller.register_widget(office_gal)
controller.register_widget(office_guy)
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
controller.register_widget(laundry)
controller.register_screen(mock)
#controller.register_screen(mock_continuous)
controller.register_screen(gdrive)
controller.register_screen(epaper)
