from bs4 import BeautifulSoup
from quietpaper import logger
import requests

class SmogWidget:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.data = False
        self.is_smog = False

    def initialize(self):
        pass
        
    def retrieve(self, cycle):
        try:
            self.data = requests.get('http://www.stuttgart.de/feinstaubalarm/widget/xtrasmall').text
            self.is_smog = BeautifulSoup(self.data, 'html.parser').find('div', {'class': 'alarm-on'})
        except Exception as e: 
            logger.warning("Cannot retrieve SmogWidget: " + (e.message if hasattr(e, 'message') else type(e).__name__))
        
    def get_retrieve_rate(self, cycle):
        return 60*6
    
    def get_render_rate(self, cycle):
        return 60

    def render(self, display, cycle):
        x = self.x
        y = self.y
        display.erase(x, y, x+32, y+32)
        if self.is_smog:
            display.bmp(x, y, "icons/allergy_smog.bmp", is_red=True)
