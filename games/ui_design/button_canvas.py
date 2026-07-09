# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: ui_design\button_canvas.py
from tkinter import Canvas, PhotoImage, Event
from PIL import Image, ImageTk, ImageEnhance
from audio_play import audio
import gui.language as language
from functools import partial

class Button_Canvas:

    def __init__(self, canvas, x1, y1, x2, y2, text, fontsize=15, d_outline='gray', d_fill='gray', image=None, rect_vir_bord=3, btn_type='other', no_out_line=True, zone_out=1, zone_in=1, image_path='', anchor='center', command=None, no_frame_img=False):
        self.canvas = canvas
        self.value = text
        self.tag = text + str(y2)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.d_outline = d_outline
        self.d_fill = d_fill
        if no_out_line:
            rect_width = 0
            rect_in_width = 0
        else:
            rect_width = 2
            rect_in_width = 1
        rect_vir_bord = rect_vir_bord
        self.focus = False
        self.btn_type = btn_type
        self.image_id = None
        if image != None:
            self.canvas.create_image(((x1 + x2) // 2), ((y1 + y2) // 2), image=image, tag=(self.tag))
        self.image_path = image_path
        self.no_frame_img = no_frame_img
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        self.image_id = self.create_image_bg((x1 + x2) / 2, (y1 + y2) / 2, width, height)
        self.rec = self.canvas.create_rectangle(x1, y1, x2, y2, width=rect_width, outline=(self.d_outline), tag=(self.tag))
        self.rec_in = self.canvas.create_rectangle((x1 + rect_vir_bord), (y1 + rect_vir_bord), (x2 - rect_vir_bord), (y2 - rect_vir_bord),
          width=rect_in_width, outline=(self.d_outline), tag=(self.tag))
        coors_x = (x1 + x2) // 2
        coors_y = (y1 + y2) // 2
        if anchor == "sw":
            coors_x = x1
            coors_y = y2
        else:
            if anchor == "w":
                coors_x = x1
            self.anchor = anchor
            self.tex = self.canvas.create_text(coors_x, coors_y, text=(self.value), font=("STKaiti", fontsize), fill=(self.d_fill),
              tag=(self.tag),
              width=(x2 - x1),
              anchor=anchor)
            self.fontsize = fontsize
            self.zone_in = zone_in
            self.zone_out = zone_out
            self.command = command

    def create_image_bg(self, image_x, image_y, type_width, type_height):
        image_bg_id = None
        if self.image_path != "":
            image_title = Image.open(self.image_path)
            image_title = image_title.resize((round(type_width), round(type_height)), Image.ANTIALIAS)
            self.image_bg = ImageTk.PhotoImage(image_title)
            image_bg_id = self.canvas.create_image(image_x, image_y, image=(self.image_bg), tag=(self.tag))
        if not self.no_frame_img:
            path_img_bgm_frame = "./photo/new/introduce_rect.PNG"
            image_title = Image.open(path_img_bgm_frame)
            image_title = image_title.resize((round(type_width), round(type_height)), Image.ANTIALIAS)
            self.image_bg_frame = ImageTk.PhotoImage(image_title)
            self.image_frame_id = self.canvas.create_image(image_x, image_y, image=(self.image_bg_frame), tag=(self.tag))
        return image_bg_id

    def update_image_bg(self, scale):
        width = self.x2 - self.x1
        width *= scale
        width_mid = (self.x2 + self.x1) / 2
        height = self.y2 - self.y1
        height *= scale
        height_mid = (self.y2 - self.y1) / 2
        image_title = Image.open(self.image_path)
        image_title = image_title.resize((round(width), round(height)), Image.ANTIALIAS)
        enhancer = ImageEnhance.Brightness(image_title)
        bright_image = enhancer.enhance(scale * scale ** scale)
        self.image_bg = ImageTk.PhotoImage(bright_image)
        self.canvas.itemconfig((self.image_id), image=(self.image_bg))
        path_img_bgm_frame = "./photo/new/introduce_rect.PNG"
        image_title = Image.open(path_img_bgm_frame)
        image_title = image_title.resize((round(width), round(height)), Image.ANTIALIAS)
        enhancer = ImageEnhance.Brightness(image_title)
        bright_image = enhancer.enhance(scale * scale ** scale)
        self.image_bg_frame = ImageTk.PhotoImage(bright_image)
        self.canvas.itemconfig((self.image_frame_id), image=(self.image_bg_frame))

    def update_layout_size(self, scale):
        width = self.x2 - self.x1
        width *= scale
        width_mid = (self.x2 + self.x1) / 2
        height = self.y2 - self.y1
        height *= scale
        height_mid = (self.y2 + self.y1) / 2
        self.canvas.coords(self.rec, width_mid - width / 2, height_mid - height / 2, width_mid + width / 2, height_mid + height / 2)
        self.canvas.coords(self.rec_in, width_mid - width / 2, height_mid - height / 2, width_mid + width / 2, height_mid + height / 2)
        fontsize = round(self.fontsize * scale)
        self.canvas.itemconfig((self.tex), font=(language.FONT_WORD, fontsize))
        if self.anchor == "sw":
            self.canvas.coords(self.tex, width_mid - width / 2, height_mid + height / 2)
        else:
            if self.anchor == "w":
                self.canvas.coords(self.tex, width_mid - width / 2, height_mid)
            else:
                self.canvas.coords(self.tex, width_mid, height_mid)
        self.update_image_bg(scale)

    def focus_on(self, color: str, voice=True):
        self.canvas.itemconfig((self.rec), outline=color)
        self.canvas.itemconfig((self.rec_in), outline=color)
        self.canvas.itemconfig((self.tex), fill=color)
        self.focus = True
        if voice:
            audio.Audio().play("./audio/destination.mp3")
        if self.zone_out != 1:
            self.update_layout_size(self.zone_out)
        if self.command is not None:
            self.command()

    def focus_off(self):
        self.canvas.itemconfig((self.rec), outline=(self.d_outline))
        self.canvas.itemconfig((self.rec_in), outline=(self.d_outline))
        self.canvas.itemconfig((self.tex), fill=(self.d_fill))
        self.focus = False
        if self.zone_in != 1:
            self.update_layout_size(self.zone_in)

    @classmethod
    def Focus(cls, event: Event, obj_list, color: str):
        one_of_obj_is_focus = False
        last_focus = None
        for self in obj_list:
            if self.focus:
                last_focus = self
            if self.x1 <= event.x <= self.x2:
                if self.y1 <= event.y <= self.y2:
                    one_of_obj_is_focus = self.focus or True
                    self.focus_on(color)

        if one_of_obj_is_focus:
            if last_focus is not None:
                last_focus.focus_off()

    def move_on(self, color: str):
        self.canvas.itemconfig((self.rec), outline=color)
        self.canvas.itemconfig((self.rec_in), outline=color)
        self.canvas.itemconfig((self.tex), fill=color)

    def move_off(self):
        self.canvas.itemconfig((self.rec), outline=(self.d_outline))
        self.canvas.itemconfig((self.rec_in), outline=(self.d_outline))
        self.canvas.itemconfig((self.tex), fill=(self.d_fill))

    @classmethod
    def Move(cls, event: Event, color: str):
        for self in cls.obj_btn:
            if self.x1 <= event.x <= self.x2:
                if self.y1 <= event.y <= self.y2:
                    self.move_on(color)
            else:
                self.move_off()

    def execute(self, event: Event, function=None):
        if self.x1 <= event.x <= self.x2:
            if self.y1 <= event.y <= self.y2:
                self.focus_off()
                self.move_off()
                if function != None:
                    return function()

    def click(self, event: Event):
        if self.x1 <= event.x <= self.x2:
            if self.y1 <= event.y <= self.y2:
                return True

    def value_change(self, value: str):
        self.value = value
        self.canvas.itemconfig((self.tex), text=(self.value))

    def destroy(self):
        self.canvas.delete(self.tag)

# okay decompiling /games/climb/climb_source_code/ui_design/button_canvas.pyc
