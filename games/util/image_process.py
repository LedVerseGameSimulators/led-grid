# Source Generated with Decompyle++
# File: image_process.pyc (Python 3.7)

from PIL import ImageTk, Image

class ImageProcess:
    
    def __init__(self):
        pass

    
    def generate(self, img_path, width, height):
        width = round(width)
        height = round(height)
        image_background = Image.open(img_path)
        image_background = image_background.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image_background)

    
    def open_img(self, img_path, width, height):
        width = round(width)
        height = round(height)
        image_background = Image.open(img_path)
        image_background = image_background.resize((width, height), Image.LANCZOS)
        return image_background

    
    def crop_img(self, img_path, width, height, region):
        width = round(width)
        height = round(height)
        img_opened = self.open_img(img_path, width, height)
        img_crop = img_opened.crop(region)
        return ImageTk.PhotoImage(img_crop)


