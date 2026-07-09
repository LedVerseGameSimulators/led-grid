# Source Generated with Decompyle++
# File: gui_util.pyc (Python 3.7)

from tkinter import Canvas, Toplevel, Tk
from PIL import Image, ImageTk
from game_play import life_value_calculation as life
list_image = [
    None] * int(life.LifeValueCalculation.ALL_LIFE_VALUE / life.LifeValueCalculation.ONE_LIFE_VALUE)
full_screen = True

def canvas_create_image(image_file, bg_image_file):
    '''
    canvas = Canvas(root, width=scnWidth, height=scnHeight, bg=\'black\')
    image = Image.open("./photo/white_heart.png")
    image = image.resize((int(scnWidth / 10), int(scnHeight / 6)), Image.ANTIALIAS)
    image_file = ImageTk.PhotoImage(image)
    # image_file = PhotoImage(file="./photo/white_heart.png")

    for i in range(life.LifeValueCalculation.ALL_LIFE_VALUE):
        list_image[i] = canvas.create_image(int(scnWidth / 20) + i * int(scnWidth / 10), int(scnHeight / 12) + 10,
                                            image=image_file)  # anchor=\'n\',

    canvas.pack()
    '''
    root = Toplevel()
    root.attributes('-fullscreen', full_screen)
    (scnWidth, scnHeight) = root.maxsize()
    canvas = Canvas(root, scnWidth, scnHeight, 'black', **('width', 'height', 'bg'))
    None(None, (lambda event = None: screen_mouse_event(event, root)))
    image = Image.open('./photo/white_heart.png')
    image = image.resize((int(scnWidth / 10), int(scnHeight / 6)), Image.ANTIALIAS)
    image_file = ImageTk.PhotoImage(image)
    image = Image.open('./photo/caise.png')
    image = image.resize((int(scnWidth), int(scnHeight)), Image.ANTIALIAS)
    bg_image_file = ImageTk.PhotoImage(image)
    list_image = [
        None] * life.LifeValueCalculation.ALL_LIFE_VALUE
    canvas.create_image(int(scnWidth / 2), int(scnHeight / 2), bg_image_file, **('image',))
    for i in range(life.LifeValueCalculation.ALL_LIFE_VALUE):
        list_image[i] = canvas.create_image(int(scnWidth / 10) + i * int(scnWidth / 5), int(scnHeight / 12) + 10, image_file, **('image',))
    
    canvas.pack()
    return (root, canvas)


def screen_mouse_event(event, root):
    global full_screen
    full_screen = not full_screen
    root.attributes('-fullscreen', full_screen)

border = 1
side_ = 25

def update_life_value_ui(canvas, life_value):
    for i in range(life.LifeValueCalculation.ALL_LIFE_VALUE - 1, life_value - 1, -1):
        if list_image[i] is not None:
            canvas.delete(list_image[i])
            list_image[i] = None


def draw_rect_in_canvas(canvas, led_col, led_row):
    width = led_col * side_
    high = led_row * side_
    if canvas is not None:
        color = (254, 254, 254)
        cell_width = width / led_col
        cell_height = high / led_row
        for row in range(led_row):
            for col in range(led_col):
                left = col * (cell_width + border) + border
                top = row * (cell_height + border) + border
                color_ = '#' + '{:02X}'.format(color[0]) + '{:02X}'.format(color[1]) + '{:02X}'.format(color[2])
                canvas.create_rectangle(left, top, left + int(cell_width), top + int(cell_height), color_, **('fill',))
            
        


def write_text_in_rectangle(canvas, coors, led_col, led_row, text = ('',)):
    row = coors[0]
    col = coors[1]
    width = led_col * side_
    high = led_row * side_
    if canvas is not None:
        cell_width = width / led_col
        cell_height = high / led_row
        left = col * (cell_width + border) + border
        top = row * (cell_height + border) + border
        if row == 0:
            top = 3
        if col == 0:
            left = 3
        canvas.create_text((2 * left + cell_width) / 2, (2 * top + cell_height) / 2, text, **('text',))

