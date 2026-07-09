# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.14.4 (main, Apr  7 2026, 13:13:20) [Clang 17_iter__iter_ (clang-1700.6.4.2)]
# Embedded file name: gui_player_login.py
import random, sys, time, tkinter
from tkinter import ttk, messagebox
import loguru
from PIL import ImageTk, Image
from loguru import logger
from encryption import yanqian
from gui.gui_countdown import GuiCountDown
from gui.gui_editor_game import EditorGame
from gui.gui_game_result import GameResult
import gui.language as language
from model.setting import Setting
from ui_design.button_canvas import Button_Canvas
from ui_design.entry_canvas import Entry_Canvas
from util.image_process import ImageProcess
from functools import partial
import datetime

class PlayerLogin:

    def on_screen_click_level_btn(self, event, list_button):
        color = "#66ffff"
        for idx, button in enumerate(list_button):
            if button.click(event):
                button.focus_on(color)
                if idx == 0 and self.cb_player_num:
                    self.cb_player_num.place(x=((button.x1 + button.x2) / 2), y=((button.y1 + button.y2) / 2), anchor="w")
            else:
                button.focus_off()

        self.keyboardinput = ""

    def on_screen_keypress(self, event, list_button):
        for item in list_button:
            if item.focus:
                str_char = "{0}".format(event.char)
                item.input(str_char)

        self.keyboardinput += event.char

    def player_canvas_return(self, event, list_player, list_button):
        if self.parent.card_scan:
            card_id = self.keyboardinput
            phone_num = card_id
            list_phone = self.list_phone
            if phone_num == "":
                return
            result = 0
            if self.db:
                result = self.db.search_custom_by_field("card_id", phone_num)
            else:
                messagebox.showerror((language.GAME_PROMPT), (language.SEVER_IP + language.NO_EXIST),
                  parent=(self.root))
                self.keyboardinput = ""
                return
                if len(result) != 1:
                    messagebox.showerror((language.GAME_PROMPT), (language.GAME_CUSTOM + language.NO_EXIST),
                      parent=(self.root))
                    self.keyboardinput = ""
                    return
            idx_phone = 1
            idx_time = -3
            phone_num = result[0][idx_phone]
            try:
                result = self.db.search_custom_by_phone(phone_num)
                count = list_phone.count(phone_num)
                count += 1
                custom_time_left = round(float(result[0][idx_time]) - self.game_time * count, 2)
            except:
                messagebox.showerror((language.GAME_PROMPT), (language.GAME_CUSTOM + phone_num + language.NO_EXIST),
                  parent=(self.root))
                self.keyboardinput = ""
                return
            else:
                if custom_time_left < 0:
                    messagebox.showerror((language.GAME_PROMPT), (language.GAME_CUSTOM + phone_num + language.GAME_INSUFFICIENT),
                      parent=(self.root))
                    self.keyboardinput = ""
                    return
                list_phone.append(phone_num)
                player_info = result[0][2] + ":" + phone_num + "-" + language.TIME_LEFT + language.COLON + str(custom_time_left)
                list_player.append(card_id)
                self.keyboardinput = ""
                canvas = event.widget
                i = len(list_button)
                type_height = canvas.winfo_height() / 22
                type_width = canvas.winfo_width() * 1 / 3
                type_boder = canvas.winfo_height() / 60
                y1_start = canvas.winfo_height() * 5 / 20
                x1 = canvas.winfo_width() / 2 - type_width / 2
                y1 = i * type_height + i * type_boder + y1_start
                x2 = x1 + type_width
                y2 = int(y1 + type_height)
                bt_game_type = Button_Canvas(canvas, x1, y1, x2, y2, player_info, 12,
                  d_outline="gray", d_fill="gray", rect_vir_bord=1)
                list_button.append(bt_game_type)

    def player_canvas_double_click(self, event, list_canvas_button):
        canvas = event.widget
        event.x = canvas.canvasx(event.x)
        event.y = canvas.canvasy(event.y)
        for i, button in enumerate(list_canvas_button.copy()):
            if button.click(event):
                list_canvas_button.remove(button)
                self.list_player.pop(i)
                self.list_phone.pop(i)
            button.destroy()

        self.root.update()
        self.list_phone.clear()
        list_canvas_button.clear()
        tmp_list_player_info = self.list_player.copy()
        self.list_player.clear()
        for card_id in tmp_list_player_info:
            self.keyboardinput = card_id
            self.player_canvas_return(event, self.list_player, list_canvas_button)

    def update_finish_button_image(self):
        curWidth, curHeight = self.root_size
        canvas = self.canvas
        color_display = 1
        list_size = [0.9, 1]
        image_title = Image.open("./photo/240515/buttons_PNG17.png")
        image_title = image_title.resize((round(curWidth * 0.1 * list_size[int(color_display)]),
         round(curHeight * 0.1 * list_size[int(color_display)])), Image.LANCZOS)
        self.image_game_level_button = ImageTk.PhotoImage(image_title)
        canvas.itemconfig("game_level_button", image=(self.image_game_level_button))

    def update_parent(self):
        if self.cur_level == 1:
            str_level = language.LEVAL_SIMPLE
        else:
            if self.cur_level == 2:
                str_level = language.LEVAL_NORMAL
            else:
                str_level = language.LEVAL_HARDER
        self.parent.level_button.value_change(str_level)
        self.parent.update_self_value_after_edit()

    def ui_init_main_img_bgm(self):
        img_process = self.img_process
        canvas = self.canvas
        size = self.root_size
        scnWidth, scnHeight = size
        path_img_bgm1 = "./photo/game_main.png"
        self.image_game_level_bg = img_process.generate(path_img_bgm1, round(size[0]), round(size[1]))
        canvas.create_image((size[0] / 2), (size[1] / 2), anchor="center", image=(self.image_game_level_bg))
        path_img_ranking_frame = "./photo/new/result_ranking_bg_frame1.png"
        self.img_ranking_frame = img_process.generate(path_img_ranking_frame, scnWidth * 4 / 5, scnHeight * 3 / 5)
        canvas.create_image((scnWidth / 2), (scnHeight * 4 / 10), anchor="center", image=(self.img_ranking_frame), tag="background")
        path_img_ranking_bg_trans = "./photo/new/barcode_bd.png"
        self.img_ranking_bg_trans = img_process.generate(path_img_ranking_bg_trans, scnWidth * 4 / 5, scnHeight * 3 / 5)
        canvas.create_image((scnWidth / 2), (scnHeight * 4 / 10), anchor="center", image=(self.img_ranking_bg_trans), tag="background")

    def display_player_info(self, list_player_info_button, list_player_info):
        canvas = self.canvas
        list_new_button = []
        for i in range(len(list_player_info_button)):
            button = list_player_info_button[i]
            type_height = canvas.winfo_height() / 22
            type_width = canvas.winfo_width() * 1 / 3
            type_boder = canvas.winfo_height() / 60
            y1_start = canvas.winfo_height() * 5 / 20
            x1 = canvas.winfo_width() / 2 - type_width / 2
            y1 = i * type_height + i * type_boder + y1_start
            x2 = x1 + type_width
            y2 = int(y1 + type_height)
            bt_game_type = Button_Canvas(canvas, x1, y1, x2, y2, (list_player_info[i - 1]), 12,
              d_outline="gray", d_fill="gray", rect_vir_bord=1)
            list_new_button.append(bt_game_type)

        self.list_button = list_new_button

    def on_combobox_select(self, event):
        widget = event.widget
        self.canvas.focus_set()
        widget.place_forget()
        self.list_input_btn[0].info = widget.get()
        self.list_input_btn[0].update(widget.get())

    def create_button(self):
        self.tv_cb_player_num = tkinter.IntVar(value=(self.player_nums))
        self.cb_player_num = ttk.Combobox((self.canvas), textvariable=(self.tv_cb_player_num), values=[1, 2, 3, 4, 5, 6], width=4)
        self.cb_player_num.bind("<<ComboboxSelected>>", self.on_combobox_select)

    def __init__(self, parent):
        root = tkinter.Toplevel()
        root.attributes("-fullscreen", Setting.FULL_SCREEN)
        size = root.maxsize()
        scnWidth = curWidth = size[0]
        scnHeight = curHeight = size[1]
        self.root_size = (curWidth, curHeight)
        self.cur_level = parent.cur_level
        card_scan = parent.card_scan
        self.parent = parent
        self.db = parent.db
        self.game_time = parent.parent.game_time
        self.player_nums = parent.parent.setting.player_num.get()
        self.life_value = parent.parent.life_value
        self.list_game_level_btn_img_bgm_path = [
         "./photo/game_type/1star.jpg", "./photo/game_type/2star.jpg",
         "./photo/game_type/3star.jpg"]
        fm_main = tkinter.Frame(root)
        fm_main.pack()
        canvas = tkinter.Canvas(fm_main, width=curWidth, height=curHeight, borderwidth=0, highlightthickness=0)
        canvas.pack(anchor="center")
        self.list_btn_backornext = []
        self.list_input_btn = []
        self.list_player, self.list_button, self.list_phone = [], [], []
        self.keyboardinput = ""
        canvas.bind("<Button-1>", lambda event: self.on_screen_click_level_btn(event, self.list_btn_backornext))
        canvas.bind("<KeyPress>", lambda event: self.on_screen_keypress(event, self.list_input_btn))
        canvas.bind("<Return>", lambda event: self.player_canvas_return(event, self.list_player, self.list_button))
        canvas.bind("<Double-Button-1>", lambda event: self.player_canvas_double_click(event, self.list_button))
        self.canvas = canvas
        canvas.focus_set()
        self.img_process = ImageProcess()
        self.ui_init_main_img_bgm()
        path_img_title_frame_btn = "./photo/new/ranking_list_head_frame.png"
        wid_title = scnWidth / 6
        hei_title = scnHeight / 10
        x1, y1 = curWidth / 2 - wid_title / 2, curHeight * 1 / 10 - hei_title / 2
        x2, y2 = curWidth / 2 + wid_title / 2, curHeight * 1 / 10 + hei_title / 2
        self.bt_title_frame = Button_Canvas(canvas, x1, y1, x2, y2, (language.PLAYER_LIST), (int(0.015625 * scnWidth)),
          d_outline="#1e90ff", d_fill="white", btn_type="game_type", image=None,
          image_path=path_img_title_frame_btn,
          no_frame_img=True)
        num_input_wid = wid_title / 2.6
        num_input_hei = hei_title / 2
        x1, y1 = curWidth / 2 - num_input_wid / 2, curHeight * 2 / 10 - num_input_hei / 2
        x2, y2 = curWidth / 2 + num_input_wid / 2, curHeight * 2 / 10 + num_input_hei / 2
        bt_num_input = Entry_Canvas(canvas, ((x1 + x2) / 2), ((y1 + y2) / 2), num_input_wid,
          num_input_hei,
          text1=(str(self.player_nums)), text2=(str(self.player_nums)), d_fill="#3399ff",
          fontsize=(int(0.0078125 * scnWidth)),
          outlineboder=0,
          flag=(str(1)),
          text3=(language.GAME_PLAYER_NUM))
        player_editable = parent.parent.setting.player_num_editable.get()
        bt_num_input.editable(False)
        self.cb_player_num = None
        if player_editable:
            self.create_button()
        self.list_input_btn.append(bt_num_input)
        self.list_btn_backornext.append(bt_num_input)
        size = self.root_size
        btn_width = size[0] / 12
        btn_height = size[1] / 12
        btn_back_x = size[0] / 7 - btn_width / 2
        btn_back_y = size[1] * 6 / 8
        btn_next_x = size[0] - btn_back_x - btn_width
        btn_next_y = size[1] * 6 / 8
        partial_back = partial(self.back)
        partial_next = partial(self.next)
        path_button_frame = "./photo/new/result_ranking_bg_frame1.PNG"
        btn_back = Button_Canvas(canvas, btn_back_x, btn_back_y, (btn_back_x + btn_width), (btn_back_y + btn_height), (language.BACK),
          (int(0.010416666666666666 * scnWidth)),
          d_outline="#1e90ff", d_fill="white", btn_type="game_type", image=None,
          image_path=path_button_frame,
          zone_out=1.05,
          zone_in=0.95,
          command=partial_back)
        btn_next = Button_Canvas(canvas, btn_next_x, btn_next_y, (btn_next_x + btn_width), (btn_next_y + btn_height), (language.NEXT),
          (int(0.010416666666666666 * scnWidth)),
          d_outline="#1e90ff", d_fill="white", btn_type="game_type", image=None,
          image_path=path_button_frame,
          zone_out=1.05,
          zone_in=0.95,
          command=partial_next)
        self.list_btn_backornext += [btn_back, btn_next]
        if not card_scan:
            pst_x = scnWidth / 2
            pst_y = btn_back_y + btn_height / 2
            num_input_wid = scnWidth / 8
            num_input_hei = scnHeight / 15
            bt_num_input = Entry_Canvas(canvas, pst_x, pst_y, num_input_wid,
              num_input_hei,
              text1="", text2=(language.USER), d_fill="#3399ff",
              fontsize=(int(0.010416666666666666 * scnWidth)),
              outlineboder=0,
              flag=(str(2)))
            self.list_input_btn.append(bt_num_input)
            self.list_btn_backornext.append(bt_num_input)
        self.root = root
        root.update()
        scnWidth, scnHeight = root.maxsize()
        curWidth = scnWidth
        curHeight = scnHeight
        tmpcnf = "+%d+%d" % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol("WM_DELETE_WINDOW", self.customized_function)
        root.iconbitmap("./photo/ledplay.ico")
        root.title(language.GAME_LEVAL)
        logger.info("in gui player login")

    def next(self):
        player_num = int(self.list_input_btn[0].value)
        if len(self.list_input_btn) > 1:
            tourist_name = self.list_input_btn[1].value
            GuiCountDown(self.parent.parent, self, player_num, tourist_name, self.list_phone)
        else:
            if self.parent.card_scan and player_num > 0 and len(self.list_phone) >= player_num:
                GuiCountDown((self.parent.parent), self, player_num_cur=player_num, list_player_cur=(self.list_phone))
            else:
                messagebox.showerror((language.GAME_PLAYER), (language.NO_SET), parent=(self.root))
        loguru.logger.info("out of gui countdown")

    def back(self):
        loguru.logger.info("game player login ui back button click")
        self.root.update()
        time.sleep(0.3)
        self.list_btn_backornext[0].focus_off()
        self.root.destroy()

    def customized_function(self):
        self.root.destroy()
        self.parent.customized_function()

# okay decompiling /Users/apple/Desktop/activerse/climb/climb_source_code/gui/gui_player_login.pyc
