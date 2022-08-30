from quietpaper.iot import epd7in5b
from quietpaper.iot import epd7in5bv2
from quietpaper.iot import epd7in5b_HD
from PIL import Image

class EpaperScreen:
    def __init__(self, version=1):
        self.version = version
        if version == 2:
            self.epd = epd7in5bv2.EPD()
            self.screen_width = epd7in5bv2.EPD_WIDTH
            self.screen_height = epd7in5bv2.EPD_HEIGHT
        elif version == 3:
            self.epd = epd7in5b_HD.EPD()
            self.screen_width = epd7in5b_HD.EPD_WIDTH
            self.screen_height = epd7in5b_HD.EPD_HEIGHT
        else:
            self.epd = epd7in5b.EPD()
            self.screen_width = epd7in5b.EPD_WIDTH
            self.screen_height = epd7in5b.EPD_HEIGHT
        self.screen_image_red = Image.new('1', (self.screen_width, self.screen_height), 255)
        self.screen_image_black = Image.new('1', (self.screen_width, self.screen_height), 255)
        self.epd.init()
        
    def get_update_rate(self, cycle):
        if cycle.is_slow:
            return 30
        else:
            return 5

    def update(self, display, cycle):
        display_width, display_height = display.red_image.size
        offset = ((self.screen_width - display_width) // 2, (self.screen_height - display_height) // 2)
        self.screen_image_black.paste(display.black_image, offset)
        self.screen_image_red.paste(display.red_image, offset)
        self.epd.display(self.epd.getbuffer(self.screen_image_black), self.epd.getbuffer(self.screen_image_red))

    def clear(self, display):
        display.clear()
        if self.version == 3:
            self.epd.Clear()
        else:
            self.epd.Clear(0xFF)