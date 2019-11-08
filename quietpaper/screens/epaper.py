from quietpaper.iot import epd7in5b

class EpaperScreen:
    def __init__(self):
        self.epd = epd7in5b.EPD()
        self.epd.init()
        
    def get_update_rate(self, cycle):
        if cycle.is_slow:
            return 30
        else:
            return 5

    def update(self, display, cycle):
        self.epd.display(self.epd.getbuffer(display.black_image), self.epd.getbuffer(display.red_image))

    def clear(self, display):
        display.clear()
        self.epd.Clear(0xFF)