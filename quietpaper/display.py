from PIL import Image, ImageDraw, ImageFont

class Display:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.black_image = Image.new('1', (self.width, self.height), 255)
        self.red_image = Image.new('1', (self.width, self.height), 255)
        self.bmp_cache = {}
        self.black_canvas = ImageDraw.Draw(self.black_image)
        self.red_canvas = ImageDraw.Draw(self.red_image)
        self.font = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 18)

    def text(self, x, y, text, is_red=False, font=None):
        canvas = self.red_canvas if is_red else self.black_canvas
        canvas.text((x, y), text, font=self.font if font is None else font, fill=0)

    def bmp(self, x, y, url, is_red=False):
        bmp = self.bmp_cache.get(url, Image.open(url))
        image = self.red_image if is_red else self.black_image
        image.paste(bmp, (x, y))
        self.bmp_cache[url] = bmp

    def line(self, x1, y1, x2, y2, is_red=False):
        canvas = self.red_canvas if is_red else self.black_canvas
        canvas.line((x1, y1, x2, y2), fill=0)

    def erase(self, x1, y1, x2, y2):
        self.black_canvas.rectangle((x1, y1, x2, y2), fill=255)
        self.red_canvas.rectangle((x1, y1, x2, y2), fill=255)

    def clear(self):
        self.erase(0, 0, self.width, self.height)