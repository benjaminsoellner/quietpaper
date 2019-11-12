import googlemaps
import json
import datetime
import pprint
import itertools
from quietpaper import logger

QP_COMMUTE_NUM_ROUTES = 3

def is_train(step):
    return step["travel_mode"] == "TRANSIT" and step["transit_details"]["line"]["vehicle"]["type"] == "COMMUTER_TRAIN"

def is_bus(step):
    return step["travel_mode"] == "TRANSIT" and step["transit_details"]["line"]["vehicle"]["type"] == "BUS"

def get_departure(step):
    return datetime.datetime.fromtimestamp(step["transit_details"]["departure_time"]["value"])

def get_arrival(leg):
    return datetime.datetime.fromtimestamp(leg["arrival_time"]["value"])

def parse_route(legs):
    steps = [leg["steps"] for leg in legs]
    route = {"bus": None, "train": None, "city": None}
    for step in list(itertools.chain.from_iterable(steps)):
        if is_bus(step) and route["bus"] is None:
            route["bus"] = get_departure(step)
        elif is_train(step) and route["train"] is None:
            route["train"] = get_departure(step)
    if route["train"] is not None:
        route["city"] = get_arrival(legs[-1]) if len(legs)>0 else None
    return route

class CommuteWidget:

    def __init__(self, api_key_file, from_loc, to_loc, leave_for_bus, leave_for_train, x, y):
        self.api_key = json.load(open(api_key_file, "r"))["key"]
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.num_routes = QP_COMMUTE_NUM_ROUTES
        self.leave_for_bus = leave_for_bus
        self.leave_for_train = leave_for_train
        self.x = x
        self.y = y
        self.data = []
        self.routes = []

    def initialize(self):
        self.gmaps = googlemaps.client.Client(key=self.api_key)
        self.data = []
        self.routes = []
        
    def retrieve(self, cycle):
        start_time = datetime.datetime.now()
        known_departure = None if len(self.routes) == 0 \
            else self.routes[0]["bus"] if self.routes[0]["bus"] is not None else self.routes[0]["train"]
        if known_departure is not None and known_departure > start_time:
            return
        try:
            self.data = []
            self.routes = []
            routes_found = 0
            trials = 0
            too_late = False
            fallback_route = None
            while routes_found < self.num_routes and trials < 10 and not too_late:
                trials += 1
                data = self.gmaps.directions(self.from_loc, self.to_loc, mode="transit", departure_time=start_time)
                routes = [parse_route(route["legs"]) for route in data]
                self.data.append(data)
                for route in routes:
                    if route is not None and route["train"] is not None:
                        if routes_found == self.num_routes-1:
                            if sum([1 for route in self.routes+[route] if route["bus"] is not None]) > 0:
                                append_route = True
                            else:
                                fallback_route = route
                                append_route = False
                        else:
                            append_route = True
                        if append_route:
                            routes_found += 1
                            self.routes.append(route)
                        new_start_time = route["bus"] if route["bus"] is not None else route["train"]
                        if new_start_time != start_time:
                            start_time = new_start_time
                        else:
                            too_late = True
            if routes_found < self.num_routes and fallback_route is not None:
                self.routes.append(fallback_route)
        except Exception as e: 
            logger.warning("Cannot retrieve CommuteWidget: " + (e.message if hasattr(e, 'message') else type(e).__name__))
    
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
        display.erase(x, y, x+302, y+136)
        if sum([1 for route in self.routes if route["bus"] is not None]) > 0:
            display.bmp(x,    y,     "icons/commute_bus.bmp")
        if len(self.routes) > 0:
            display.bmp(x+11, y+52,  "icons/commute_train.bmp")
            display.bmp(x+23, y+104, "icons/commute_city.bmp")
        offset = 0
        for route in self.routes:
            if route["bus"] is not None:
                time = route["bus"]
                display.text(x+46+offset, y+7, time.strftime("%H:%M"), time < deadline_bus)
            time = route["train"]
            display.text(x+46+11+offset, y+7+52, time.strftime("%H:%M"), time < deadline_train and route["bus"] is None)
            time = route["city"]
            display.text(x+46+23+offset, y+7+104, time.strftime("%H:%M"))
            offset += 77