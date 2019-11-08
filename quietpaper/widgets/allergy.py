from quietpaper.iot.airctrl import AirClient
import sys, os

class AllergyWidget:
    
    def __init__(self, purifier_host, x, y):
        self.x = x
        self.y = y
        self.purifier_host = purifier_host
        self.air_client = AirClient(purifier_host)
        self.idx_inside = None
        self.idx_inside_bad = False
        self.idx_outside = None
        self.idx_outside_bad = False

    def initialize(self):
        pass
        
    def retrieve(self, cycle):
        try:
            status = self.air_client.get_status(output=False)
            self.idx_inside = status['iaql']
            self.idx_inside_bad = (int(self.idx_inside) > 5)
        except:
            self.idx_inside = None
            self.idx_inside_bad = False
        # TODO: retrieve for outside allergy index from https://www.polleninfo.org/DE/de/prognose/vorhersage.html
        
    def get_retrieve_rate(self, cycle):
        return 1
    
    def get_render_rate(self, cycle):
        return 1

    def render(self, display, cycle):
        x = self.x
        y = self.y
        display.erase(x, y, x+270, y+32)
        if self.idx_inside is not None:
            display.bmp(x+184, y, "icons/allergy_inside.bmp", is_red=self.idx_inside_bad)
            display.text(x+230, y+7, str(self.idx_inside), is_red=self.idx_inside_bad)
        # TODO: display for outside allergy index