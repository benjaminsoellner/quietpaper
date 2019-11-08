from PIL import Image, ImageDraw, ImageFont
import numpy as np

class MockScreen:
    def __init__(self, logbmp_url):
        self.logbmp_url = logbmp_url

    def get_update_rate(self, cycle):
        return 5
    
    def update(self, display, cycle):
        result = np.full((display.height, display.width, 3), 255, 'uint8')
        black = np.array(display.black_image)
        red = np.array(display.red_image)
        blacks = (black == 0)
        reds = (red == 0)
        result[...,0:3][reds] = (255,0,0)
        result[...,0:3][blacks] = (0,0,0)
        display.black_image.save(self.logbmp_url)
        image = Image.fromarray(result, mode="RGB")
        image.save(self.logbmp_url)

    def clear(self, display):
        display.clear()
        self.update(display, None)

        