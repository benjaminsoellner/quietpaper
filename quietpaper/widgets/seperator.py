class Seperator:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def initialize(self):
        pass
        
    def retrieve(self, cycle):
        pass
        
    def get_retrieve_rate(self, cycle):
        return None
    
    def get_render_rate(self, cycle):
        return None

    def render(self, display, cycle):
        display.erase(self.x1, self.y1, self.x2, self.y2)
        display.line(self.x1, self.y1, self.x2, self.y2)