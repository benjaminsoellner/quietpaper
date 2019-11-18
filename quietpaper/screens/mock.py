from PIL import Image, ImageDraw, ImageFont
import numpy as np
import datetime

def get_combined_image(black_image, red_image):
    result = np.full((black_image.height, black_image.width, 3), 255, 'uint8')
    black = np.array(black_image)
    red = np.array(red_image)
    blacks = (black == 0)
    reds = (red == 0)
    result[...,0:3][reds] = (255,0,0)
    result[...,0:3][blacks] = (0,0,0)
    image = Image.fromarray(result, mode="RGB")
    return image


class MockScreen:
    def __init__(self, png_url, add_date=False):
        self.png_url = png_url
        self.add_date = add_date

    def get_update_rate(self, cycle):
        return 5
    
    def update(self, display, cycle):
        if self.add_date:
            print(self.png_url)
            url = self.png_url % datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        else:
            url = self.png_url
        image = get_combined_image(display.black_image, display.red_image)
        image.save(url, "PNG")

    def clear(self, display):
        display.clear()
        self.update(display, None)