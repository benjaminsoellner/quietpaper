import googlemaps
import datetime
import requests
from quietpaper import logger
from dateutil import tz
from dateutil import parser
from PIL import ImageFont

QP_COMMUTE_NUM_ROUTES = 3
QP_COMMUTE_SMALL_FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 12)
QP_TRANSITOUS_URL = "https://api.transitous.org/api/v6/plan"

class TransitousCommuteStrategy:
    def __init__(self, commute_from, commute_to, bus_stations, train_stations):
        self.commute_from = commute_from
        self.commute_to = commute_to
        self.bus_stations = bus_stations
        self.train_stations = train_stations

    def initialize(self, commute_widget):
        pass

    def _retrieve_from_transitous(self):
        params = {
           "fromPlace": f'{self.commute_from["latitude"]},{self.commute_from["longitude"]}',
           "toPlace": f'{self.commute_to["latitude"]},{self.commute_to["longitude"]}'
        }
        headers = {"User-Agent": "https://github.com/benjaminsoellner/quietpaper"}
        response = requests.get(QP_TRANSITOUS_URL, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json().get("itineraries", {})

    def retrieve(self, commute_widget):
        try:
            journeys = self._retrieve_from_transitous()
            routes = []
            for journey in journeys[:(3 if len(journeys) > 3 else len(journeys))]:
                route = {
                    "bus": None,
                    "bus_station": None,
                    "bus_delay": 0,
                    "train": None,
                    "train_station": None,
                    "train_delay": 0,
                    "city": None,
                    "city_delay": 0
                }
                for leg in journey["legs"]:
                    mode = leg.get("mode", "")
                    name = leg.get("routeShortName", "")
                    leg_from = leg.get("from", {})
                    leg_to = leg.get("to", {})
                    origin = leg_from.get("name", "")
                    departure = parser.parse(leg_from["departure"]).astimezone(tz.tzlocal()) if "departure" in leg_from else None
                    scheduled_departure = parser.parse(leg_from["scheduledDeparture"]).astimezone(tz.tzlocal()) if "scheduledDeparture" in leg_from else None
                    departure_delay = (departure - scheduled_departure).total_seconds() if departure is not None and scheduled_departure is not None else 0
                    arrival = parser.parse(leg_to["arrival"]).astimezone(tz.tzlocal()) if "arrival" in leg_to else None
                    scheduled_arrival = parser.parse(leg_to["scheduledArrival"]).astimezone(tz.tzlocal()) if "scheduledArrival" in leg_to else None
                    arrival_delay = (arrival - scheduled_arrival).total_seconds() if arrival is not None and scheduled_arrival is not None else 0
                    if arrival is None or departure is None:
                        route = None
                        break
                    if route["bus"] is None and route["train"] is None and ((mode == "BUS" or name.startswith("Bus")) and "SEV" not in name):
                        route["bus"] = departure
                        route["bus_delay"] = departure_delay/60 if departure_delay is not None else 0
                        route["bus_station"] = self.bus_stations.get(origin, "*")
                        if route["bus_station"] == "*":
                            logger.warning("Unknown bus station found: %s" % origin)
                    elif route["train"] is None and (mode in ["TRAIN", "TRAM", "SUBURBAN"] or "SEV" in name):
                        route["train"] = departure
                        route["train_delay"] = departure_delay/60 if departure_delay is not None else 0
                        route["train_station"] = self.train_stations.get(origin, "*")
                        if route["train_station"] == "*":
                            logger.warning("Unknown train station found: %s" % origin)
                    route["city"] = arrival
                    route["city_delay"] = arrival_delay/60 if arrival_delay is not None else 0
                if route is not None:
                    routes.append(route)
            commute_widget.data = journeys
            commute_widget.routes = routes
        except Exception as e: 
            logger.warning(f"Cannot retrieve TransitousCommuteStrategy: {e}")

class CommuteWidget:

    def __init__(self, strategy, leave_for_bus, leave_for_train, x, y):
        self.leave_for_bus = leave_for_bus
        self.leave_for_train = leave_for_train
        self.strategy = strategy
        self.x = x
        self.y = y
        self.data = []
        self.routes = []
        self.num_routes = QP_COMMUTE_NUM_ROUTES

    def initialize(self):
        self.strategy.initialize(self)
        self.data = []
        self.routes = []
        
    def retrieve(self, cycle):
        self.strategy.retrieve(self)
    
    def get_retrieve_rate(self, cycle):
        return 5 * (6 if cycle.is_slow else 1)
    
    def get_render_rate(self, cycle):
        return 1

    def render(self, display, cycle):
        now = datetime.datetime.now()
        deadline_bus   = now + datetime.timedelta(minutes=self.leave_for_bus)
        deadline_train = now + datetime.timedelta(minutes=self.leave_for_train)
        x = self.x
        y = self.y
        display.erase(x, y, x+326, y+136)
        if sum([1 for route in self.routes if route["bus"] is not None]) > 0:
            display.bmp(x,    y,     "icons/commute_bus.bmp")
        if len(self.routes) > 0:
            display.bmp(x+11, y+52,  "icons/commute_train.bmp")
            display.bmp(x+23, y+104, "icons/commute_city.bmp")
        offset = 0
        for route in self.routes:
            bus_station = "" if "bus_station" not in route or route["bus_station"] is None else route["bus_station"]
            train_station = "" if "train_station" not in route or route["train_station"] is None else route["train_station"]
            bus_delay = "" if "bus_delay" not in route or route["bus_delay"] == 0 else ("+%d" % route["bus_delay"])
            train_delay = "" if "train_delay" not in route or route["train_delay"] == 0 else ("+%d" % route["train_delay"])
            city_delay = "" if "city_delay" not in route or route["city_delay"] == 0 else ("+%d" % route["city_delay"])
            if route["bus"] is not None:
                is_red = route["bus"].replace(tzinfo=tz.tzlocal()) < deadline_bus.replace(tzinfo=tz.tzlocal())
                bus_station_offset = (7 if bus_station != "" else 0)
                if bus_station != "":
                    display.text(x+46+offset, y+13, bus_station, is_red, font=QP_COMMUTE_SMALL_FONT)
                display.text(x+46+offset+bus_station_offset, y+7, route["bus"].strftime("%H:%M"), is_red)
                if bus_delay != "":
                    display.text(x+46+offset+bus_station_offset+44, y+13, bus_delay, is_red, font=QP_COMMUTE_SMALL_FONT)
            if route["train"] is not None:
                is_red = route["train"].replace(tzinfo=tz.tzlocal()) < deadline_train.replace(tzinfo=tz.tzlocal()) and route["bus"] is None
                train_station_offset = (7 if train_station != "" else 0)
                if train_station != "":
                    display.text(x+46+11+offset, y+13+52, train_station, is_red, font=QP_COMMUTE_SMALL_FONT)
                display.text(x+46+11+offset+train_station_offset, y+7+52, route["train"].strftime("%H:%M"), is_red)
                if train_delay != "":
                    display.text(x+46+11+offset+train_station_offset+44, y+13+52, train_delay, is_red, font=QP_COMMUTE_SMALL_FONT)
            if route["city"] is not None:
                display.text(x+46+23+offset, y+7+104, route["city"].strftime("%H:%M"))
                if city_delay != "":
                    display.text(x+46+23+offset+44, y+13+104, city_delay, font=QP_COMMUTE_SMALL_FONT)
            offset += 85
