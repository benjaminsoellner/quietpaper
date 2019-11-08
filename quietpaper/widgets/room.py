import datetime 

class RoomWidget:

    def __init__(self, tado_connection, zone, max_humidity, bmp_name, x, y):
        self.tado_connection = tado_connection
        self.zone = zone
        self.max_humidity = max_humidity
        self.bmp_name = bmp_name
        self.x = x
        self.y = y
        self.last_open = None

    def initialize(self):
        self.tado_connection.init_home()
        
    def retrieve(self, cycle):
        data = self.tado_connection.query_home("zones/%d/state" % self.zone)
        self.data = data
        self.temperature = data["sensorDataPoints"]["insideTemperature"]["celsius"]
        self.temp_setting = None if data["setting"]["power"] == "OFF" else data["setting"]["temperature"]["celsius"]
        self.humidity = data["sensorDataPoints"]["humidity"]["percentage"]
        self.window_open = data["openWindow"] is not None
        if self.window_open:
            self.window_last_open = datetime.datetime.now()
        else:
            self.window_last_open = None
        
    def get_retrieve_rate(self, cycle):
        return 5
    
    def get_render_rate(self, cycle):
        return 5

    def render(self, display, cycle):
        now = datetime.datetime.now()
        x = self.x
        y = self.y
        last_open = self.window_last_open
        if self.window_open:
            window_bmp = "icons/window_open.bmp"
        elif last_open is not None and last_open.day == now.day and last_open.year == now.year and last_open.month == now.month:
            window_bmp = None
        else:
            window_bmp = "icons/window_closed.bmp"
        if self.temp_setting is not None and self.temperature > self.temp_setting:
            arrow_bmp = "icons/arrow_down.bmp"
        elif self.temp_setting is not None and self.temperature < self.temp_setting:
            arrow_bmp = "icons/arrow_up.bmp"
        else:
            arrow_bmp = None
        room_bmp = "icons/room_%s.bmp" % self.bmp_name
        display.erase(x, y, x+290, y+32)
        display.bmp(x, y, room_bmp)
        if window_bmp is not None:
            display.bmp(x+37, y, window_bmp)
        display.text(x+76, y+7, "%d°C" % self.temperature)
        if arrow_bmp is not None:
            display.bmp(x+125, y, arrow_bmp)
        humidity_too_high = self.humidity > self.max_humidity
        display.text(x+167, y+7, "%d%%" % self.humidity, is_red=humidity_too_high)