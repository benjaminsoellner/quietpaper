import googlemaps
import json
import datetime
import dateutil.parser
import pprint
import itertools
from quietpaper import logger
import urllib.request, urllib.parse
import json 
from dateutil import tz

QP_COMMUTE_NUM_ROUTES = 3

class HafasCommuteStrategy:

    def __init__(self, hafas_glue_url, from_address, from_latitude, from_longitude, to_address, to_latitude, to_longitude, 
                    via_station, bus_preferred_station, train_preferred_station):
        self.hafas_glue_service = hafas_glue_url
        self.from_latitude = from_latitude
        self.to_latitude = to_latitude
        self.from_address = from_address
        self.to_address = to_address
        self.from_longitude = from_longitude
        self.to_longitude = to_longitude
        self.via_station = via_station
        self.bus_preferred_station = bus_preferred_station
        self.train_preferred_station = train_preferred_station

    def initialize(self, commute_widget):
        pass

    def _parse_route(self, route):
        arrival = None
        result = {"bus": None, "train": None, "city": None, "bus_preferred_station": None, "train_preferred_station": None}
        for leg in route["legs"]:
            is_bus = "line" in leg and leg["line"]["mode"] == "bus"
            is_train = "line" in leg and leg["line"]["mode"] == "train"
            is_bus_preferred_station = is_bus and leg["origin"]["name"] == self.bus_preferred_station
            is_train_preferred_station = is_train and leg["origin"]["name"] == self.train_preferred_station
            departure = dateutil.parser.parse(leg["departure"])
            if is_bus and result["bus"] is None:
                result["bus"] = departure
                result["bus_preferred_station"] = is_bus_preferred_station
            elif is_train and result["train"] is None:
                result["train"] = departure
                result["train_preferred_station"] = is_train_preferred_station
            arrival = dateutil.parser.parse(leg["arrival"])
        if result["train"] is not None:
            result["city"] = arrival
        return result

    def retrieve(self, commute_widget):
        try:
            now = datetime.datetime.now() 
            vals = [self.from_address, self.from_latitude, self.from_longitude, self.to_address, self.to_latitude, self.to_longitude, str(int(now.timestamp())), str(commute_widget.num_routes), self.via_station]
            args = [urllib.parse.quote(val.encode('utf-8')) for val in vals]
            suffix = "?from_address={}&from_latitude={}&from_longitude={}&to_address={}&to_latitude={}&to_longitude={}&departure={}&num_routes={}&via_station={}"
            hafas_url = self.hafas_glue_service + suffix.format(*args)
            with urllib.request.urlopen(hafas_url) as hafas_call:
                commute_widget.data = json.loads(hafas_call.read().decode())
                routes = [self._parse_route(route) for route in commute_widget.data]
                commute_widget.routes = [route for route in routes if route["city"] is not None]
        except Exception as e: 
            logger.warning("Cannot retrieve HafasCommuteStrategy: " + (e.message if hasattr(e, 'message') else type(e).__name__))


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
        display.erase(x, y, x+302, y+136)
        if sum([1 for route in self.routes if route["bus"] is not None]) > 0:
            display.bmp(x,    y,     "icons/commute_bus.bmp")
        if len(self.routes) > 0:
            display.bmp(x+11, y+52,  "icons/commute_train.bmp")
            display.bmp(x+23, y+104, "icons/commute_city.bmp")
        offset = 0
        for route in self.routes:
            is_bus_preferred_station = "bus_preferred_station" not in route or \
                route["bus_preferred_station"] is None or \
                route["bus_preferred_station"] == True
            is_train_preferred_station = "train_preferred_station" not in route or \
                route["train_preferred_station"] is None or \
                route["train_preferred_station"]
            if route["bus"] is not None:
                time = route["bus"]
                text = time.strftime("%H:%M")
                text += "" if is_bus_preferred_station else "*"
                is_red = time.replace(tzinfo=tz.tzlocal()) < deadline_bus.replace(tzinfo=tz.tzlocal())
                display.text(x+46+offset, y+7, text, is_red)
            time = route["train"]
            text = time.strftime("%H:%M")
            text += "" if is_train_preferred_station else "*"
            is_red = time.replace(tzinfo=tz.tzlocal()) < deadline_train.replace(tzinfo=tz.tzlocal()) and route["bus"] is None
            display.text(x+46+11+offset, y+7+52, text, is_red)
            time = route["city"]
            display.text(x+46+23+offset, y+7+104, time.strftime("%H:%M"))
            offset += 77
