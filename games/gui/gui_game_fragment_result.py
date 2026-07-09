# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.14.4 (main, Apr  7 2026, 13:13:20) [Clang 17_iter__iter_ (clang-1700.6.4.2)]
# Embedded file name: gui_game_fragment_result.py
import logging, random, sys, time, tkinter, traceback
from threading import Thread
from tkinter import ttk
import loguru
from PIL import ImageTk, Image
from gui.gui_countdown import GuiCountDown
from gui.gui_game_result import GameResult
from gui.gui_player_login import PlayerLogin
import gui.language as language
from model.setting import Setting
from ui_design.button_canvas import Button_Canvas
from ui_design.entry_canvas import Entry_Canvas
from util.image_process import ImageProcess
from functools import partial

class GameFragmentRst:

    def update_level_btn1(self):
        color = "#66ffff"
        self.list_btn_level_slt[0].image_path = self.list_game_level_btn_img_bgm_path[self.cur_level - 1]
        self.list_btn_level_slt[0].focus_on(color)

    def on_screen_click_level_slt(self, event, list_button):
        color = "#66ffff"
        for i, button in enumerate(list_button):
            if button.click(event):
                button.focus_on(color, voice=False)
                self.cur_level = i + 1
            else:
                button.focus_off()

        self.update_level_btn1()

    def on_screen_click_level_btn(self, event, list_button):
        color = "#66ffff"
        for button in list_button:
            if button.click(event):
                button.focus_on(color)
            else:
                button.focus_off()

    def on_screen_click_back_next_btn(self, event, list_button):
        color = "#66ffff"
        for button in list_button:
            if not button.focus:
                if button.click(event):
                    button.focus_on(color)
                else:
                    button.focus_off()

    def on_screen_keypress(self, event, list_button):
        for item in list_button:
            if item.focus:
                str_char = "{0}".format(event.char)
                item.input(str_char)

    def get_list_size_rate(self, cur_level):
        select_size_rate = 1.15
        unselect_size_rate = (3 - select_size_rate) / 2
        list_size_rate = [1, 1, 1]
        for idx, rate in enumerate(list_size_rate):
            if idx == cur_level - 1:
                list_size_rate[idx] *= select_size_rate
            else:
                list_size_rate[idx] *= unselect_size_rate

        return list_size_rate

    def create_game_level_slt(self, frame, list_game_type):
        scnWidth, scnHeight = self.root_size
        img_process = self.img_process
        self.list_canvas_button = []
        self.list_list_btn.append(self.list_canvas_button)
        canvas = tkinter.Canvas(frame, width=scnWidth, height=(scnHeight / 4), borderwidth=0, highlightthickness=0)
        canvas.pack(anchor="center")
        if self.editable:
            canvas.bind("<Button-1>", lambda event: self.on_screen_click_level_slt(event, self.list_canvas_button))
        path_img_bgm1 = "./photo/game_main.png"
        region = (0, 0, scnWidth, scnHeight / 4)
        time_bft = time.time()
        self.image_file_game_list = img_process.crop_img(path_img_bgm1, scnWidth, scnHeight, region)
        canvas.create_image(0, 0, anchor="nw", image=(self.image_file_game_list), tag="background")
        print(time.time() - time_bft)
        list_game_type_img_bgm_path = [
         "./photo/game_type/simple.jpeg", "./photo/game_type/normal.jpeg",
         "./photo/game_type/difficult.jpeg"]
        main_canvas = canvas
        type_width = scnWidth / 6
        game_type_width_mid_list = [0.25 * scnWidth, 0.5 * scnWidth, 0.75 * scnWidth]
        type_height = scnHeight / 7.2
        game_type_height_mid = 0.5 * scnHeight / 8 * 2.5
        for i in range(len(list_game_type)):
            y1 = game_type_height_mid - type_height / 2
            y2 = game_type_height_mid + type_height / 2
            x1 = game_type_width_mid_list[i] - type_width / 2
            x2 = game_type_width_mid_list[i] + type_width / 2
            bt_game_type = Button_Canvas(main_canvas, x1, y1, x2, y2, (list_game_type[i]), 25,
              d_outline="#1e90ff", d_fill="#3399ff", btn_type="game_type", image=None,
              image_path=(list_game_type_img_bgm_path[i]),
              zone_out=1.2,
              zone_in=0.9333333333333332,
              anchor="sw")
            if i == self.cur_level - 1:
                bt_game_type.focus_on("#66ffff", voice=False)
            self.list_canvas_button.append(bt_game_type)

    def create_game_level_fix(self, frame, cur_level):
        scnWidth, scnHeight = self.root_size
        img_process = self.img_process
        canvas = tkinter.Canvas(frame, width=scnWidth, height=(scnHeight / 4), borderwidth=0, highlightthickness=0)
        canvas.pack(anchor="center")
        path_img_bgm1 = "./photo/game_main.png"
        region = (0, 0, scnWidth, scnHeight / 4)
        self.img_level_fix_bg = img_process.crop_img(path_img_bgm1, scnWidth, scnHeight, region)
        canvas.create_image(0, 0, anchor="nw", image=(self.image_file_game_list), tag="background")
        self.img_level_fix = []
        img_level_fix = self.img_level_fix
        path_game_level_fix = "./photo/game_type/start.jpeg"
        type_width = scnWidth / 10
        type_height = scnWidth / 11.6
        game_type_width_mid_list = [
         0.25 * scnWidth, 0.5 * scnWidth, 0.75 * scnWidth]
        game_type_height_mid = 0.5 * scnHeight / 8 * 2.5
        for i in range(cur_level):
            img_level_fix.append(img_process.generate(path_game_level_fix, round(type_width), round(type_height)))
            canvas.create_image((game_type_width_mid_list[i]), game_type_height_mid, anchor="center", image=(img_level_fix[i]), tag="background")

    def command_level_btn_slt(self):
        self.fm_picture_2.grid_forget()
        self.fm_picture_1.grid(row=0, column=0)

    def command_level_btn_fix(self):
        self.fm_picture_1.grid_forget()
        self.fm_picture_2.grid(row=0, column=0)

    def create_level_select_button(self, frame, cur_level=1):
        list_button_name = [
         language.LEVAL, language.GAME_LIFE, language.GAME_TIME, language.AGILE]
        self.list_btn_level_slt = []
        self.list_list_btn.append(self.list_btn_level_slt)
        path_button_frame = "./photo/new/introduce_rect.PNG"
        list_game_type_img_bgm_path = self.list_game_level_btn_img_bgm_path
        scnWidth, scnHeight = self.root_size
        img_process = self.img_process
        canvas_height = scnHeight * 4 / 20
        canvas = tkinter.Canvas(frame, width=scnWidth, height=canvas_height, borderwidth=0, highlightthickness=0)
        canvas.pack(anchor="center")
        canvas.focus_set()
        canvas.bind("<Button-1>", lambda event: self.on_screen_click_level_btn(event, self.list_btn_level_slt))
        self.list_input_btn = []
        canvas.bind("<KeyPress>", lambda event: self.on_screen_keypress(event, self.list_input_btn))
        path_img_bgm1 = "./photo/game_main.png"
        region = (0, scnHeight / 4, scnWidth, scnHeight / 4 + canvas_height)
        self.img_level_slt_btn_bg = img_process.crop_img(path_img_bgm1, scnWidth, scnHeight, region)
        canvas.create_image(0, 0, anchor="nw", image=(self.img_level_slt_btn_bg), tag="background")
        type_width = scnWidth / 13.5
        game_type_width_mid_list = [0.25 * scnWidth, 0.4166666666666667 * scnWidth, 0.5833333333333334 * scnWidth, 0.75 * scnWidth]
        type_height = scnHeight / 20
        game_type_height_mid = 0.5 * scnHeight / 8 * 1.8
        btn_level_select = partial(self.command_level_btn_slt)
        btn_level_fix = partial(self.command_level_btn_fix)
        list_partial = [btn_level_select, None, None, btn_level_fix]
        for i in range(len(list_button_name)):
            y1 = game_type_height_mid - type_height / 2
            y2 = game_type_height_mid + type_height / 2
            x1 = game_type_width_mid_list[i] - type_width / 2
            x2 = game_type_width_mid_list[i] + type_width / 2
            if i == 0 or i == 3:
                bt_game_type = Button_Canvas(canvas, x1, y1, x2, y2, (list_button_name[i]), 15,
                  d_outline="#1e90ff", d_fill="#3399ff", btn_type="game_type", image=None,
                  image_path=(list_game_type_img_bgm_path[cur_level - 1]),
                  zone_out=1.05,
                  zone_in=0.95,
                  anchor="w",
                  command=(list_partial[i]))
            else:
                if i == 1:
                    bt_game_type = Entry_Canvas(canvas, ((x1 + x2) / 2), ((y1 + y2) / 2), type_width,
                      type_height,
                      text1=(str(self.life_value)), text2=(str(self.life_value)), d_fill="#3399ff",
                      fontsize=(int(0.0078125 * scnWidth)),
                      outlineboder=0,
                      flag=(str(i)),
                      text3=(list_button_name[i]),
                      image_path=path_button_frame)
                    bt_game_type.editable(self.blood_editable)
                    self.list_input_btn.append(bt_game_type)
                else:
                    bt_game_type = Entry_Canvas(canvas, ((x1 + x2) / 2), ((y1 + y2) / 2), type_width,
                      type_height,
                      text1=(str(self.game_time)), text2=(str(self.game_time)), d_fill="#3399ff",
                      fontsize=(int(0.0078125 * scnWidth)),
                      outlineboder=0,
                      flag=(str(i)),
                      text3=(list_button_name[i]),
                      image_path=path_button_frame)
                    bt_game_type.editable(self.time_editable)
                    self.list_input_btn.append(bt_game_type)
            self.list_btn_level_slt.append(bt_game_type)

    def create_ranking_image(self):
        scnWidth, scnHeight = self.root_size
        img_process = self.img_process
        canvas = self.canvas_ranking
        path_img_bgm1 = "./photo/game_main.png"
        path_img_ranking_frame = "./photo/new/result_ranking_bg_frame1.png"
        path_img_ranking_title_btn = "./photo/new/ranking_list_head_frame.png"
        path_img_ranking_num1 = "./photo/new/result_ranking_one_frame.png"
        path_img_ranking_num2 = "./photo/new/result_ranking_two_frame.png"
        path_img_ranking_num3 = "./photo/new/result_ranking_three_frame.png"
        path_img_ranking_num4 = "./photo/new/result_ranking_four_frame.png"
        path_img_ranking_num5 = "./photo/new/result_ranking_five_frame.png"
        path_img_ranking_num6 = "./photo/laser/result_ranking_six_frame.png"
        list_path_img_ranking = [path_img_ranking_num1, path_img_ranking_num2, path_img_ranking_num3, 
         path_img_ranking_num4, 
         path_img_ranking_num5, path_img_ranking_num6]
        self.img_ranking_bg = img_process.generate(path_img_bgm1, scnWidth, scnHeight)
        canvas.create_image(0, 0, anchor="nw", image=(self.img_ranking_bg), tag="background")
        self.img_ranking_frame = img_process.generate(path_img_ranking_frame, scnWidth * 0.8, scnHeight * 0.8)
        canvas.create_image((scnWidth / 2), (scnHeight / 2), anchor="center", image=(self.img_ranking_frame), tag="background")
        self.img_ranking_ranking_title_btn = img_process.generate(path_img_ranking_title_btn, scnWidth / 8, scnHeight / 13)
        canvas.create_image((scnWidth / 2), (scnHeight / 4.6), anchor="n", image=(self.img_ranking_ranking_title_btn), tag="background")
        canvas.create_text((scnWidth / 2), (scnHeight / 3.9), text=(language.PLAY_RANKING_LIST), font=(
         "STKaiti", int(0.0078125 * scnWidth)),
          fill="white")
        width_start = 11
        tmp = 2.3
        bank_height = scnHeight * 2.2 / 32
        bank_width = scnWidth / 3
        ranking_num = 5
        list_text = []
        for i in range(len(self.list_score)):
            if self.list_bullet[i] > 0:
                str_tmp = "{:12s}".format(self.list_player_name[i]) + "{:15s}".format("        ") + (f"{self.list_score[i]}")
                list_text.append((self.list_score[i], str_tmp))
            else:
                str_tmp = "{:12s}".format(self.list_player_name[i]) + "{:15s}".format("        ") + (f"{self.list_score[i]}")
                list_text.append((self.list_score[i], str_tmp))

        list_text = sorted(list_text, key=(lambda x: x[0]), reverse=True)
        self.list_img_ranking_bg = []
        ranking_num = len(list_text)
        for i in range(ranking_num):
            if not i == ranking_num - 1:
                if i == ranking_num - 2:
                    bank_height = scnHeight * 2.2 / 32 * 2.2 / 3
                x1, y1 = scnWidth / 2 - bank_width / 2, scnHeight * (width_start + i * tmp) / 32 - bank_height / 2
                x2, y2 = scnWidth / 2 + bank_width / 2, scnHeight * (width_start + i * tmp) / 32 + bank_height / 2
                rank_btn = Button_Canvas(canvas, x1, y1, x2, y2, (list_text[i][1]), 15,
                  d_outline="#1e90ff", d_fill="#3399ff", no_out_line=True, image=None,
                  image_path=(list_path_img_ranking[i]),
                  no_frame_img=True)
                self.list_img_ranking_bg.append(rank_btn)

        size = self.root_size
        btn_width = size[0] / 12
        btn_height = size[1] / 12
        btn_back_x = size[0] - 1.2 * btn_width
        btn_back_y = size[1] * 7 / 8
        btn_next_x = size[0] - btn_back_x - btn_width
        btn_next_y = size[1] * 3 / 8
        partial_back = partial(self.customized_function)
        partial_next = partial(self.player_login)
        path_button_frame = "./photo/new/result_ranking_bg_frame1.PNG"
        btn_back = Button_Canvas(canvas, btn_back_x, btn_back_y, (btn_back_x + btn_width), (btn_back_y + btn_height), (language.BACK),
          20,
          d_outline="#1e90ff", d_fill="#3399ff", btn_type="game_type", image=None,
          image_path=path_button_frame,
          zone_out=1.05,
          zone_in=0.95,
          command=partial_back)
        self.list_btn_backornext += [btn_back]

    def create_ranking(self, frame):
        scnWidth, scnHeight = self.root_size
        img_process = self.img_process
        self.list_btn_backornext = []
        canvas = tkinter.Canvas(frame, width=scnWidth, height=scnHeight, borderwidth=0, highlightthickness=0)
        canvas.pack(anchor="center")
        canvas.bind("<Button-1>", lambda event: self.on_screen_click_back_next_btn(event, self.list_btn_backornext))
        self.canvas_ranking = canvas
        try:
            self.create_ranking_image()
        except:
            loguru.logger.error(traceback.format_exc())

    def ui_init_main_img_bgm(self):
        img_process = self.img_process
        canvas = self.canvas
        size = self.root_size
        path_img_bgm1 = "./photo/game_main.png"
        self.image_game_level_bg = img_process.generate(path_img_bgm1, round(size[0]), round(size[1]))
        time_bft = time.time()
        canvas.create_image((size[0] / 2), (size[1] / 2), anchor="center", image=(self.image_game_level_bg))
        print("gen img bg", time.time() - time_bft)

    def title_canvas_click(self, event, list_item):
        canvas = event.widget
        print("x, y", event.x, event.y)
        if canvas.gettags("current") == canvas.gettags("close"):
            self.customized_function()

    def __init__(self, parent, cur_level):
        time_bft = time.time()
        root = tkinter.Toplevel()
        root.attributes("-fullscreen", Setting.FULL_SCREEN)
        root.attributes("-topmost", "true")
        size = root.maxsize()
        curWidth = size[0]
        curHeight = size[1]
        self.root_size = (curWidth, curHeight)
        self.cur_level = cur_level
        self.parent = parent
        self.list_player_name = parent.list_player_name
        self.list_score = parent.total_scode
        self.list_bullet = parent.total_bullet
        self.list_list_btn = []
        self.list_game_level_btn_img_bgm_path = [
         "./photo/game_type/1star.jpg", "./photo/game_type/2star.jpg",
         "./photo/game_type/3star.jpg"]
        fm_main = tkinter.Frame(root)
        fm_main.pack()
        canvas = tkinter.Canvas(fm_main, width=curWidth, height=curHeight, borderwidth=0, highlightthickness=0)
        canvas.pack(anchor="center")
        canvas.bind("<Button-1>", lambda event: self.title_canvas_click(event))
        self.canvas = canvas
        fm_picture_2 = tkinter.Frame(canvas)
        fm_picture_2.grid(row=0, column=0)
        fm_picture_1 = tkinter.Frame(canvas)
        fm_picture_1.grid(row=0, column=0)
        fm_button = tkinter.Frame(canvas)
        fm_button.grid(row=2, column=0)
        fm_ranking = tkinter.Frame(canvas)
        fm_ranking.grid(row=3, column=0)
        self.fm_picture_1 = fm_picture_1
        self.fm_picture_2 = fm_picture_2
        self.img_process = ImageProcess()
        self.ui_init_main_img_bgm()
        self.create_ranking(fm_ranking)
        self.root = root
        root.update()
        scnWidth, scnHeight = root.maxsize()
        curWidth = scnWidth
        curHeight = scnHeight
        tmpcnf = "+%d+%d" % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol("WM_DELETE_WINDOW", self.customized_function)
        root.iconbitmap("./photo/ledplay.ico")
        root.title(language.GAME_RANK)
        loguru.logger.info("in gui game fragment result")
        time_tmp = int(parent.setting.game_result_show_time.get())
        while parent.circle_game and self.root and time_tmp > 0:
            time.sleep(0.05)
            time_tmp -= 0.05
            self.root.update()

        root.destroy()
        root = None

    def player_login(self):
        self.parent.life_value = int(self.list_input_btn[0].value)
        self.parent.game_level = self.cur_level
        if self.parent.game_record_rt.game_time_pass == 0:
            self.parent.game_time = float(self.list_input_btn[1].value)
            self.parent.page3 = PlayerLogin(self)
            self.list_btn_backornext[1].focus_off()
            loguru.logger.info("out of gui PlayerLogin")
        else:
            GuiCountDown(self.parent, self)
            loguru.logger.info("out of gui countdown")

    def back(self):
        loguru.logger.info("game fragment result back button click")
        self.list_btn_backornext.clear()
        self.customized_function()

    def customized_function(self):
        self.root.destroy()
        self.root = None

# okay decompiling /Users/apple/Desktop/activerse/climb/climb_source_code/gui/gui_game_fragment_result.pyc
