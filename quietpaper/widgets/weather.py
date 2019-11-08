from PIL import ImageFont
import datetime
import requests
import json

QP_WEATHER_ICONS_FONT = ImageFont.truetype("fonts/meteocons-webfont.ttf", 28)
QP_WEATHER_ICONS_MAP  = {u"01d":u"B",u"01n":u"C",u"02d":u"H",u"02n":u"I",u"03d":u"N",u"03n":u"N",u"04d":u"Y",u"04n":u"Y",u"09d":u"R",u"09n":u"R",u"10d":u"R",u"10n":u"R",u"11d":u"P",u"11n":u"P",u"13d":u"W",u"13n":u"W",u"50d":u"M",u"50n":u"W"}
QP_WEATHER_ICONS_BAD  = ["R", "P", "W", "M"]

class WeatherWidget:

    def __init__(self, api_key_file, zip_location, x, y):
        with open(api_key_file, "r") as fd:
            self.api_key = json.load(fd)["key"]
        self.zip_location = zip_location
        self.x = x
        self.y = y
        self.data = False
        self.is_smog = False

    def initialize(self):
        pass
        
    def retrieve(self, cycle):
        self.weather = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"appid": self.api_key, "zip": self.zip_location}).json()
        self.forecast = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={"appid": self.api_key, "zip": self.zip_location}).json()
        self.weather_icon = QP_WEATHER_ICONS_MAP[self.weather["weather"][0]["icon"]]
        self.forecast_icon = QP_WEATHER_ICONS_MAP[self.forecast["list"][0]["weather"][0]["icon"]]
        self.weather_bad = self.weather_icon in QP_WEATHER_ICONS_BAD
        self.forecast_bad = self.forecast_icon in QP_WEATHER_ICONS_BAD
        self.temp = "%d°C" % (int(self.weather["main"]["temp"])-273)
        
    def get_retrieve_rate(self, cycle):
        return 30
    
    def get_render_rate(self, cycle):
        return 30

    def render(self, display, cycle):
        x = self.x
        y = self.y
        display.erase(x, y, x+160, y+32)
        display.text(x+1,  y+1, self.weather_icon,  is_red=self.weather_bad,  font=QP_WEATHER_ICONS_FONT)
        if self.forecast_icon != self.weather_icon:
            display.text(x+38, y+1, self.forecast_icon, is_red=self.forecast_bad, font=QP_WEATHER_ICONS_FONT)
        display.text(x+77, y+7, self.temp)