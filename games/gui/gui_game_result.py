# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.14.4 (main, Apr  7 2026, 13:13:20) [Clang 17_iter__iter_ (clang-1700.6.4.2)]
# Embedded file name: gui_game_result.py
import json, shelve, time
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image
import tkinter.font as tf
import tkinter
from loguru import logger
from database.db_operation import DBOperation
from gui.gui_game_ranking_canvas import GameRankingCanvas
import gui.language as language
from gui2.ui_table import Table
from model.setting import Setting
from ui_design.button_canvas import Button_Canvas
from ui_design.entry_canvas import Entry_Canvas

class GameResult:

    def btn_comform(self):
        return

    def update_data_ui(self, scode, life_vale):
        cur_length = life_vale * self.length_rect / 100
        self.canvas.itemconfig((self.text_scode_value), text=(str(scode)))

    def title_canvas_keypress(self, event, list_item):
        canvas = event.widget
        for item in list_item:
            str_char = "{0}".format(event.char)
            event = [
             event.x, event.y]
            item.input(str_char)

    def title_canvas_click(self, event, list_item):
        canvas = event.widget
        if canvas.gettags("current") == canvas.gettags("close"):
            logger.info("game result ui close button click")
            self.customized_function()
        else:
            for item in list_item:
                str_char = "{0}".format(event.char)
                event = [
                 event.x, event.y]
                item.Focus(event, str_char=str_char)

    def draw_background(self, canvas, scnWidth, scnHeight):
        image_title = Image.open("./photo/game_result.png")
        scale_width = image_title.width
        scal_height = image_title.height
        image_title = image_title.resize((scnWidth, scnHeight), Image.ANTIALIAS)
        self.image_file_title = ImageTk.PhotoImage(image_title)
        canvas.create_image((scnWidth / 2), (scnHeight / 2), image=(self.image_file_title))
        scale_width = image_title.width / scale_width
        scal_height = image_title.height / scal_height
        image_title = Image.open("./photo/new/result_head_frame.png")
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_head_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image((0.5 * scnWidth), (0.0824074074074074 * scnHeight), image=(self.result_head_frame))
        image_title = Image.open("./photo/new/result_ranking_bg_frame1.png")
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_ranking_bg_frame1 = ImageTk.PhotoImage(image_title)
        canvas.create_image((0.5 * scnWidth), (0.5648148148148148 * scnHeight), image=(self.result_ranking_bg_frame1))
        image_title = Image.open("./photo/new/ranking_list_head_frame.png")
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.ranking_list_head_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image((0.5026041666666666 * scnWidth), (0.22407407407407406 * scnHeight), image=(self.ranking_list_head_frame))
        image_title = Image.open("./photo/new/result_ranking_bg_frame2.png")
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_ranking_bg_frame2 = ImageTk.PhotoImage(image_title)
        canvas.create_image((0.14791666666666667 * scnWidth), (0.35185185185185186 * scnHeight), image=(self.result_ranking_bg_frame2), anchor="nw")
        image_title = Image.open("./photo/new/result_grade_frame.png")
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_grade_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image((0.2390625 * scnWidth), (0.44537037037037036 * scnHeight), image=(self.result_grade_frame))
        image_title = Image.open("./photo/new/result_scode_frame.png")
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_scode_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image((0.24166666666666667 * scnWidth), (0.5722222222222222 * scnHeight), image=(self.result_scode_frame))
        image_title = Image.open("./photo/new/result_ranking_frame.png")
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_ranking_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image((0.240625 * scnWidth), (0.6944444444444444 * scnHeight), image=(self.result_ranking_frame))
        image_title = Image.open("./photo/300.png")
        image_title = image_title.resize((30, 30), Image.ANTIALIAS)
        self.image_close = ImageTk.PhotoImage(image_title)
        canvas.create_image(scnWidth, 0, anchor="ne", image=(self.image_close), tag="close")
        color_2 = "white"
        canvas.create_text((0.2390625 * scnWidth), (0.44537037037037036 * scnHeight), text=(language.LEVEL), font=(
         "STKaiti", int(0.013020833333333334 * scnWidth)),
          fill=color_2)
        canvas.create_text((0.24166666666666667 * scnWidth), (0.5722222222222222 * scnHeight), text=(language.SCORE), font=(
         "STKaiti", int(0.013020833333333334 * scnWidth)),
          fill=color_2)
        canvas.create_text((0.240625 * scnWidth), (0.6944444444444444 * scnHeight), text=(language.GAME_RANK), font=(
         "STKaiti", int(0.013020833333333334 * scnWidth)),
          fill=color_2)
        canvas.create_text((0.5020833333333333 * scnWidth), (0.22592592592592592 * scnHeight), text=(language.PLAY_RANKING_LIST), font=(
         "STKaiti", int(0.013020833333333334 * scnWidth), "bold"),
          fill=color_2)

    def __init__(self, parent, db, result=None, player_group_id=0, title=language.GAME_RESULT, game_time=1, game_player_num=1, cur_scode=0, barcode=False, parent_game_running=None):
        self.root = tkinter.Toplevel()
        root = self.root
        root.attributes("-topmost", "true")
        self.parent = parent
        self.parent_game_running = parent_game_running
        logger.info("in gui game result")
        self.parent.game_record_rt.running_to_obj = self
        if Setting.USE_SERIAL_HD:
            root.attributes("-fullscreen", True)
        color = "#CCFFFF"
        scnWidth, scnHeight = root.maxsize()
        frame_head = Frame(root)
        frame_head.pack(fill=BOTH, expand=True)
        base_line = scnHeight / 3
        canvas = Canvas(frame_head, height=base_line, width=scnWidth)
        canvas.pack(expand=True, fill=BOTH)
        self.list_item = []
        canvas.focus_set()
        canvas.bind("<KeyPress>", lambda event: self.title_canvas_keypress(event, self.list_item))
        canvas.bind("<Button-1>", lambda event: self.title_canvas_click(event, self.list_item))
        self.draw_background(canvas, scnWidth, scnHeight)
        entry_canvas = Entry_Canvas(canvas, (scnWidth / 2), (0.08333333333333333 * scnHeight), (0.125 * scnWidth), (0.05 * scnHeight), title,
          title, d_outline=color, d_fill="#66ffff", fontsize=(int(0.015625 * scnWidth)), outlineboder=0)
        entry_canvas.value = title
        self.list_item.append(entry_canvas)
        self.image_rank = []
        gap = 10
        text_color = "yellow"
        if game_time == 0:
            game_time = 1
        rank_num = len(result)
        list_text = []
        if barcode:
            for i in range(rank_num):
                try:
                    custom_id_info = result[i][4]
                    custom_id_arr = custom_id_info.split(",")
                    custom_info = ""
                    for custom_id in custom_id_arr[None[:1]]:
                        custom_info_rst = db.search_custom_tb_by_id(custom_id)
                        phone_info = custom_info_rst[0][1]
                        custom_info += phone_info[None[:3]] + "****" + phone_info[(-3)[:None]]
                        custom_info = "{:12s}".format(custom_info_rst[0][2]) + "{:15s}".format(custom_info)

                    start_width = 0.8125 * scnWidth
                    start_height = 0.4022222222222222 * scnHeight
                    scode = result[i][3]
                    list_text.append(custom_info + str(scode))
                except:
                    pass

            self.game_ranking = GameRankingCanvas(canvas, (scnWidth * 2 / 5), (scnHeight / 2), coors=[
             scnWidth * 1 / 2, scnHeight * 3 / 10],
              screen_size=(
             scnWidth, scnHeight),
              data=list_text,
              scan=barcode,
              title=False,
              bg_img_path="./photo/game_result.png")
            j = 0
            text_color = "#66ffff"
            for j in range(len(result)):
                custom_id_info = result[j][-1]
                if custom_id_info == player_group_id:
                    custom_id_info = result[j][4]
                    custom_id_arr = custom_id_info.split(",")
                    custom_info = ""
                    for custom_id in custom_id_arr[None[:1]]:
                        custom_info_rst = db.search_custom_tb_by_id(custom_id)
                        custom_info += custom_info_rst[0][2]
                        custom_info += "\n"
                        phone_info = custom_info_rst[0][1]
                        custom_info += phone_info[None[:3]] + "**" + phone_info[(-3)[:None]]
                        custom_scode = result[j][3]

                    ranking_star = round((len(result) - (j + 1)) / len(result) * 5)
                    if len(result) == 1:
                        ranking_star = 5
                    image = Image.open("./photo/xingxing.png")
                    height = 30
                    image = image.resize((height, height), Image.ANTIALIAS)
                    if ranking_star < 1:
                        ranking_star = 1
                    for i in range(ranking_star):
                        self.image_rank.append(ImageTk.PhotoImage(image))
                        start_height = 4 * scnHeight / 9
                        start_width = 443 * scnWidth / 1440
                        between_width = image.width * 1.5
                        canvas.create_image((start_width + i * between_width), start_height, image=(self.image_rank[i]))

                    start_width = 528 * scnWidth / 1440
                    start_height = 517 * scnHeight / 900
                    canvas.create_text(start_width, start_height, text=(str(custom_scode)), font=(
                     "STKaiti", int(0.020833333333333332 * scnWidth)),
                      fill=text_color)
                    start_width = 528 * scnWidth / 1440
                    start_height = 630 * scnHeight / 900
                    canvas.create_text(start_width, start_height, text=(str(j + 1)), font=(
                     "STKaiti", int(0.020833333333333332 * scnWidth)),
                      fill=text_color)
                    if self.parent.game_record_rt.game_state == Setting.GAME_NORMAL_REMOTE:
                        net_ret_result = [
                         "RESULT", self.parent_game_running.player_list[0], game_player_num,
                         self.parent_game_running.setting.game_leval.get(), game_time, cur_scode, j + 1]
                        self.parent.socket_net.send(net_ret_result)
                    break

        else:
            for i in range(rank_num):
                try:
                    custom_id_info = result[i][4]
                    custom_id_arr = custom_id_info.split(",")
                    custom_info = ""
                    for custom_id in custom_id_arr[None[:1]]:
                        custom_info_rst = db.search_custom_tb_by_id(custom_id)
                        phone_info = custom_info_rst[0][1]
                        custom_info += phone_info[None[:3]] + "****" + phone_info[(-3)[:None]]
                        custom_info = "{:10s}".format(custom_info_rst[0][2]) + "{:15s}".format(custom_info)

                    start_width = 0.8125 * scnWidth
                    start_height = 0.4022222222222222 * scnHeight
                    scode = result[i][3]
                    canvas.create_text(start_width, (start_height + i * 83 / 900 * scnHeight), text=(str(scode)), font=(
                     "STKaiti", int(0.013020833333333334 * scnWidth)),
                      fill=text_color)
                    start_width = 0.7097222222222223 * scnWidth
                    start_height = 0.4022222222222222 * scnHeight
                    canvas.create_text(start_width, (start_height + i * 83 / 900 * scnHeight), text=custom_info, font=(
                     "STKaiti", int(0.013020833333333334 * scnWidth)),
                      fill=text_color)
                except:
                    pass

            j = 0
            text_color = "#66ffff"
            for j in range(len(result)):
                custom_id_info = result[j][-1]
                scode = result[j][3]
                if cur_scode > scode:
                    custom_scode = cur_scode
                    ranking_star = round((len(result) - (j + 1)) / len(result) * 5)
                    image = Image.open("./photo/xingxing.png")
                    height = 30
                    image = image.resize((height, height), Image.ANTIALIAS)
                    if ranking_star < 1:
                        ranking_star = 1
                    for i in range(ranking_star):
                        self.image_rank.append(ImageTk.PhotoImage(image))
                        start_height = 4 * scnHeight / 9
                        start_width = 443 * scnWidth / 1440
                        between_width = image.width * 1.5
                        canvas.create_image((start_width + i * between_width), start_height, image=(self.image_rank[i]))

                    start_width = 528 * scnWidth / 1440
                    start_height = 517 * scnHeight / 900
                    canvas.create_text(start_width, start_height, text=(str(custom_scode)), font=(
                     "STKaiti", int(0.020833333333333332 * scnWidth)),
                      fill=text_color)
                    start_width = 528 * scnWidth / 1440
                    start_height = 630 * scnHeight / 900
                    canvas.create_text(start_width, start_height, text=(str(j + 1)), font=(
                     "STKaiti", int(0.020833333333333332 * scnWidth)),
                      fill=text_color)
                    if self.parent.game_record_rt.game_state == Setting.GAME_NORMAL_REMOTE:
                        net_ret_result = [
                         "RESULT", self.parent_game_running.player_list[0], game_player_num,
                         self.parent_game_running.setting.game_leval.get(), game_time, cur_scode, j + 1]
                        self.parent.socket_net.send(net_ret_result)
                    break

        root.update()
        root.state("zoomed")
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        scnWidth, scnHeight = root.maxsize()
        tmpcnf = "+%d+%d" % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol("WM_DELETE_WINDOW", self.customized_function)
        root.iconbitmap("./photo/ledplay.ico")
        while self.root:
            time.sleep(0.05)
            self.root.update()

    def customized_function(self):
        self.parent.game_record_rt.running_to_obj = None
        self.root.destroy()
        self.root = None
        if self.parent_game_running:
            self.parent_game_running.customized_function()
            a = 1

# okay decompiling /Users/apple/Desktop/activerse/climb/climb_source_code/gui/gui_game_result.pyc
