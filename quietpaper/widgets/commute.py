import googlemaps
import json
import datetime
import dateutil.parser
import itertools
import os
import subprocess
from quietpaper import logger
from dateutil import tz
from dateutil import parser
from PIL import ImageFont
from pyhafas.profile import DBProfile
from pyhafas import HafasClient
from pyhafas.types.fptf import Mode

QP_COMMUTE_NUM_ROUTES = 3
QP_COMMUTE_SMALL_FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 12)

class DBClientCommuteStrategy:
    def __init__(self, bus_stations, train_stations):
        self.bus_stations = bus_stations
        self.train_stations = train_stations
    
    def initialize(self, commute_widget):
        pass

    def _retrieve_from_dbclient(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dbclient_dir = os.path.join(script_dir, "../../dbclient")
        try:
            result = subprocess.run(
                ["/bin/bash", "--login", "-c", ". ~/.nvm/nvm.sh ; node dbclient.js"],
                cwd=dbclient_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.warning(f"dbclient.js failed with error: {e.stderr}")
            raise RuntimeError("dbclient.js process failed") from e

    def retrieve(self, commute_widget):
        try:
            journeys = self._retrieve_from_dbclient()["journeys"]
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
                    line = leg.get("line", {})
                    mode = line.get("mode", "")
                    name = line.get("name", "")
                    departure = None if leg.get("departure") is None else parser.parse(leg["departure"])
                    departure_delay = leg.get("departureDelay", 0)
                    arrival =  None if leg.get("departure") is None else parser.parse(leg["departure"])
                    arrival_delay = leg.get("arrivalDelay", 0)
                    origin = leg.get("origin", {}).get("name", "")
                    if arrival is None or departure is None:
                        route = None
                        break
                    if route["bus"] is None and route["train"] is None and (mode == "bus" or name.startswith("Bus")):
                        route["bus"] = departure
                        route["bus_delay"] = departure_delay/60 if departure_delay is not None else 0
                        route["bus_station"] = self.bus_stations.get(origin, "*")
                        if route["bus_station"] == "*":
                            logger.warning("Unknown bus station found: %s" % origin)
                    elif route["train"] is None and (mode == "train"):
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
            logger.warning(f"Cannot retrieve DBClientStrategy: {e}")

class PyhafasCommuteStrategy:

    def __init__(self, from_loc, to_loc, bus_stations, train_stations):
        try:
            self.hafas_client = HafasClient(DBProfile())
            self.from_location = self.hafas_client.locations(from_loc)[0]
            self.to_location = self.hafas_client.locations(to_loc)[0]
            self.bus_stations = bus_stations
            self.train_stations = train_stations
        except Exception as e: 
            logger.warning("Cannot initialize PyhafasCommuteStrategy: " + (e.message if hasattr(e, 'message') else type(e).__name__))

    def initialize(self, commute_widget):
        pass

    def retrieve(self, commute_widget):
        try:
            journeys = self.hafas_client.journeys(
                origin=self.from_location,
                destination=self.to_location,
                date=datetime.datetime.now()
            )
            routes = []
            for journey in journeys[:(3 if len(journeys) > 3 else len(journeys))]:
                route = {
                    "bus": None,
                    "bus_station": None,
                    "bus_delay": None,
                    "train": None,
                    "train_station": None,
                    "train_delay": None,
                    "city": None,
                    "city_delay": None
                }
                for leg in journey.legs:
                    if route["bus"] is None and route["train"] is None and (leg.mode == Mode.BUS or leg.name.startswith("Bus")):
                        route["bus"] = leg.departure
                        route["bus_delay"] = leg.departureDelay.total_seconds()/60 if leg.departureDelay is not None else 0
                        route["bus_station"] = self.bus_stations.get(leg.origin.name, "*")
                        if route["bus_station"] == "*":
                            logger.warning("Unknown bus station found: %s" % leg.origin.name)
                    elif route["train"] is None and (leg.mode == Mode.TRAIN):
                        route["train"] = leg.departure
                        route["train_delay"] = leg.departureDelay.total_seconds()/60 if leg.departureDelay is not None else 0
                        route["train_station"] = self.train_stations.get(leg.origin.name, "*")
                        if route["train_station"] == "*":
                            logger.warning("Unknown train station found: %s" % leg.origin.name)
                    route["city"] = leg.arrival
                    route["city_delay"] = leg.arrivalDelay.total_seconds()/60 if leg.arrivalDelay is not None else 0
                routes.append(route)
            commute_widget.data = journeys
            commute_widget.routes = routes
        except Exception as e: 
            logger.warning("Cannot retrieve PyhafasCommuteStrategy: " + (e.message if hasattr(e, 'message') else type(e).__name__))


class GoogleCommuteStrategy:

    def __init__(self, api_key_file, from_loc, to_loc):
        self.api_key = json.load(open(api_key_file, "r"))["key"]
        self.from_loc = from_loc
        self.to_loc = to_loc

    @staticmethod
    def _is_train(step):
        return step["travel_mode"] == "TRANSIT" and step["transit_details"]["line"]["vehicle"]["type"] == "COMMUTER_TRAIN"

    @staticmethod
    def _is_bus(step):
        return step["travel_mode"] == "TRANSIT" and step["transit_details"]["line"]["vehicle"]["type"] == "BUS"

    @staticmethod
    def _get_departure(step):
        return datetime.datetime.fromtimestamp(step["transit_details"]["departure_time"]["value"])

    @staticmethod
    def _get_arrival(leg):
        return datetime.datetime.fromtimestamp(leg["arrival_time"]["value"])

    def _parse_route(legs):
        steps = [leg["steps"] for leg in legs]
        route = {"bus": None, "train": None, "city": None}
        for step in list(itertools.chain.from_iterable(steps)):
            if GoogleCommuteStrategy._is_bus(step) and route["bus"] is None:
                route["bus"] = GoogleCommuteStrategy._get_departure(step)
            elif GoogleCommuteStrategy._is_train(step) and route["train"] is None:
                route["train"] = GoogleCommuteStrategy._get_departure(step)
        if route["train"] is not None:
            route["city"] = GoogleCommuteStrategy._get_arrival(legs[-1]) if len(legs)>0 else None
        return route

    def initialize(self, commute_widget):
        self.gmaps = googlemaps.client.Client(key=self.api_key)
    
    def retrieve(self, commute_widget):
        start_time = datetime.datetime.now()
        known_departure = None if len(commute_widget.routes) == 0 \
            else commute_widget.routes[0]["bus"] if commute_widget.routes[0]["bus"] is not None else commute_widget.routes[0]["train"]
        if known_departure is not None and known_departure > start_time:
            return
        try:
            commute_widget.data = []
            commute_widget.routes = []
            routes_found = 0
            trials = 0
            too_late = False
            fallback_route = None
            while routes_found < commute_widget.num_routes and trials < 10 and not too_late:
                trials += 1
                data = self.gmaps.directions(self.from_loc, self.to_loc, mode="transit", departure_time=start_time)
                routes = [GoogleCommuteStrategy._parse_route(route["legs"]) for route in data]
                commute_widget.data.append(data)
                for route in routes:
                    if route is not None and route["train"] is not None:
                        if routes_found == commute_widget.num_routes-1:
                            if sum([1 for route in commute_widget.routes+[route] if route["bus"] is not None]) > 0:
                                append_route = True
                            else:
                                fallback_route = route
                                append_route = False
                        else:
                            append_route = True
                        if append_route:
                            routes_found += 1
                            commute_widget.routes.append(route)
                        new_start_time = route["bus"] if route["bus"] is not None else route["train"]
                        if new_start_time != start_time:
                            start_time = new_start_time
                        else:
                            too_late = True
            if routes_found < commute_widget.num_routes and fallback_route is not None:
                self.routes.append(fallback_route)
        except Exception as e: 
            logger.warning("Cannot retrieve GoogleStrategy: " + (e.message if hasattr(e, 'message') else type(e).__name__))


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
        now = datetime.datetime.now().replace()
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
            is_red = route["train"].replace(tzinfo=tz.tzlocal()) < deadline_train.replace(tzinfo=tz.tzlocal()) and route["bus"] is None
            train_station_offset = (7 if train_station != "" else 0)
            if train_station != "":
                display.text(x+46+11+offset, y+13+52, train_station, is_red, font=QP_COMMUTE_SMALL_FONT)
            display.text(x+46+11+offset+train_station_offset, y+7+52, route["train"].strftime("%H:%M"), is_red)
            if train_delay != "":
                display.text(x+46+11+offset+train_station_offset+44, y+13+52, train_delay, is_red, font=QP_COMMUTE_SMALL_FONT)
            display.text(x+46+23+offset, y+7+104, route["city"].strftime("%H:%M"))
            if city_delay != "":
                display.text(x+46+23+offset+44, y+13+104, city_delay, is_red, font=QP_COMMUTE_SMALL_FONT)
            offset += 85

if __name__ == "__main__":
    with open("/home/dinkelpi/workspace/quietpaper/secret/_secrets.json", "r") as fd:
        secrets = json.load(fd)
    commute_bus_stations = secrets["QP_COMMUTE_BUS_STATIONS"]
    commute_train_stations = secrets["QP_COMMUTE_TRAIN_STATIONS"]
    commute_leave_for_bus = 10
    commute_leave_for_train = 30
    commute_x = 314
    commute_y = 228
    s = DBClientCommuteStrategy(commute_bus_stations, commute_train_stations)
    w = CommuteWidget(s, commute_leave_for_bus, commute_leave_for_train, commute_x, commute_y)
    s.retrieve(w)
    print(w.routes)
