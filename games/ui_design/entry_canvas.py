# Source Generated with Decompyle++
# File: entry_canvas.pyc (Python 3.7)

import subprocess
from tkinter import Canvas, Event
from tkinter.font import Font
from PIL import Image, ImageTk, ImageEnhance

class Entry_Canvas:
    
    def editable(self, flag):
        self.b_editable = flag

    
    def __init__(self, canvas, x, y, r_width, r_height, text1, text2, pw_mode, d_outline, d_fill, fontsize, outlineboder = None, flag = None, text3 = None, image_path = (False, 'gray', 'gray', 15, 2, '', '', '', False), no_frame_img = {
        'canvas': Canvas,
        'x': int,
        'y': int,
        'r_width': int,
        'r_height': int,
        'text1': str,
        'text2': str,
        'pw_mode': bool,
        'd_outline': str,
        'd_fill': str,
        'fontsize': int,
        'text3': str }):
        self.canvas = canvas
        self.focus = False
        self.mode = pw_mode
        self.b_editable = True
        self.flag = flag
        self.value = text1
        self.info = str(text1)
        self.label = text3
        self.x1 = x - r_width / 2
        self.y1 = y - r_height / 2
        self.x2 = x + r_width / 2
        self.y2 = y + r_height / 2
        self.info1 = text2
        self.info2 = text2
        self.d_outline = d_outline
        self.d_fill = d_fill
        self.keyboard = None
        self.function_var = None
        self.image_path = image_path
        self.no_frame_img = no_frame_img
        self.create_image_bg(x, y, r_width, r_height)
        self.rec = self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, outlineboder, d_outline, **('width', 'outline'))
        input_coors_x = x
        input_coors_y = y
        font = Font('STKaiti', fontsize, **('family', 'size'))
        if text3 != '':
            self.label_txt = self.canvas.create_text(self.x1, y, self.label, font, d_fill, 'w', **('text', 'font', 'fill', 'anchor'))
            input_coors_x = self.x1 + font.measure(self.label + ': ')
        self.tex = self.canvas.create_text(input_coors_x, input_coors_y, self.info1, font, d_fill, **('text', 'font', 'fill'))

    
    def create_image_bg(self, image_x, image_y, type_width, type_height):
        image_bg_id = None
        if self.image_path != '':
            image_title = Image.open(self.image_path)
            image_title = image_title.resize((round(type_width), round(type_height)), Image.ANTIALIAS)
            self.image_bg = ImageTk.PhotoImage(image_title)
            image_bg_id = self.canvas.create_image(image_x, image_y, self.image_bg, 'button_image', **('image', 'tags'))
        if not self.no_frame_img:
            path_img_bgm_frame = './photo/new/introduce_rect.png'
            image_title = Image.open(path_img_bgm_frame)
            image_title = image_title.resize((round(type_width), round(type_height)), Image.ANTIALIAS)
            self.image_bg_frame = ImageTk.PhotoImage(image_title)
            self.image_frame_id = self.canvas.create_image(image_x, image_y, self.image_bg_frame, 'button_image', **('image', 'tags'))
        return image_bg_id

    
    def update(self, text):
        self.value = text
        self.canvas.itemconfig(self.tex, text, **('text',))

    
    def update_info1(self):
        self.canvas.itemconfig(self.tex, self.info1, **('text',))

    
    def clear(self):
        self.value = ''
        self.info = ''
        self.canvas.itemconfig(self.tex, self.info1, **('text',))

    
    def focus_on(self = None, color = None):
        if self.b_editable:
            self.focus = True
            self.canvas.itemconfig(self.rec, color, **('outline',))
            self.canvas.itemconfig(self.tex, self.info + '|', **('text',))
            self.display_keyboard()

    
    def focus_off(self):
        self.focus = False
        self.canvas.itemconfig(self.rec, self.d_outline, **('outline',))
        if self.info == '':
            self.canvas.itemconfig(self.tex, self.info1, **('text',))
        else:
            self.canvas.itemconfig(self.tex, self.info, **('text',))

    
    def Focus(self = None, event_xy = None, color = None, str_char = ('white', '')):
        (event_x, event_y) = event_xy
        if event_x <= event_x or event_x <= self.x2:
            pass
        else:
            self.x1
        if event_y <= event_y or event_y <= self.y2:
            pass
        else:
            self.y1
        self.focus_on(color)
        print('Focus', str_char)
        self.focus_off()

    
    def click(self = None, event = None):
        if event.x <= event.x or event.x <= self.x2:
            pass
        else:
            self.x1
        if event.y <= event.y or event.y <= self.y2:
            pass
        else:
            self.y1
        return True

    
    def display_keyboard(self, x, y = (0, 0)):
        if self.focus:
            if x == 0:
                x = (self.x1 + self.x2) / 2
            if y == 0:
                y = (self.y1 + self.y2) / 2
            path = './use_dll/On ScreenKeyboardPortable/On-ScreenKeyboardPortable'
            self.keyboard = subprocess.Popen([
                path])

    
    def move_on(self = None, color = None):
        if self.focus == False:
            self.canvas.itemconfig(self.rec, color, **('outline',))
            if self.canvas.itemcget(self.tex, 'text') == self.info1:
                self.canvas.itemconfig(self.tex, self.info2, **('text',))

    
    def move_off(self):
        if self.focus == False:
            self.canvas.itemconfig(self.rec, self.d_fill, **('outline',))
            if self.canvas.itemcget(self.tex, 'text') == self.info2:
                self.canvas.itemconfig(self.tex, self.info1, **('text',))

    
    def Move(self = None, event = None, color = None):
        if event.x <= event.x or event.x <= self.x2:
            pass
        else:
            self.x1
        if event.y <= event.y or event.y <= self.y2:
            pass
        else:
            self.y1
        self.move_on(color)
        self.move_off()

    
    def click(self = None, event = None):
        if event.x <= event.x or event.x <= self.x2:
            pass
        else:
            self.x1
        if event.y <= event.y or event.y <= self.y2:
            pass
        else:
            self.y1
        return True

    
    def input(self = None, char = None, length = None):
        print('char', char)
        if self.focus == True:
            value = ''
            
            try:
                print(char)
                value = ord(char)
                print('value', value)
            except:
                return None

            if value == 8:
                self.value = self.value[:-1]
            elif value == '':
                self.value = ''
            elif not len(self.value) < length and char.isspace():
                self.value += char
            self.canvas.itemconfig(self.tex, self.info + '|', **('text',))

    
    def set_function(self, func = (None,), **kwargs):
        self.function_var = func
        self.function_args = kwargs

    
    def function(self):
        if self.function_var is not None:
            self.function_var(self.function_args['pwd'], self.function_args['user_entry'], self.function_args['canvas'], self.function_args['list_player'], self.function_args['list_button'], **('pwd', 'phone_num', 'canvas', 'list_player', 'list_button'))


