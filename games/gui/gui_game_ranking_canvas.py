# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: gui_game_ranking_canvas.py
import time, tkinter
from tkinter import Canvas, VERTICAL
from PIL import ImageTk, ImageGrab
import gui.language as language
from ui_design.button_canvas import Button_Canvas
from util.image_process import ImageProcess

class GameRankingCanvas:

    def __init__(self, parent_frame, width, height, bg="#66ffff", coors=[0, 0], screen_size=None, data=[], scan=False, title=True, bg_img_path="./photo/game_main.png", diff_bgi=True):
        self.diff_bgi = diff_bgi
        if scan:
            self.player_number = language.PLAYER_PHONE
        else:
            self.player_number = "  "
        image_background_path = bg_img_path
        row_1_bg_img_path = "./photo/new/result_ranking_one_frame.png"
        row_2_bg_img_path = "./photo/new/result_ranking_two_frame.png"
        row_3_bg_img_path = "./photo/new/result_ranking_three_frame.png"
        row_bg_img_path = "./photo/new/result_ranking_0_frame.png"
        img_process = ImageProcess()
        if title:
            title_width = width / 4
            title_height = height / 6
        else:
            title_width = 0
            title_height = 0
        head_size = height / 6
        relative_height = title_height + head_size
        fm_bgm_fm_size = width / 35
        ranking_width = width - 2 * fm_bgm_fm_size
        ranking_height = height - relative_height - fm_bgm_fm_size
        self.ranking_width = ranking_width
        region = (
         coors[0], coors[1],
         coors[0] + width, coors[1] + height)
        self.ranking_main_bgm = img_process.crop_img(image_background_path, screen_size[0], screen_size[1], region)
        region = (
         coors[0] + fm_bgm_fm_size, coors[1] + relative_height,
         coors[0] + fm_bgm_fm_size + ranking_width, coors[1] + relative_height + ranking_height)
        self.img_ranking_crop = img_process.crop_img(image_background_path, screen_size[0], screen_size[1], region)
        region = (
         coors[0] + width / 2 - title_width / 2, coors[1],
         coors[0] + width / 2 + title_width / 2, coors[1] + title_height)
        self.img_ranking_title = img_process.crop_img(image_background_path, screen_size[0], screen_size[1], region)
        canvas_main = Canvas(parent_frame, bg=bg, width=width, height=height, borderwidth=0)
        canvas_main.place(x=(coors[0]), y=(coors[1]), anchor="nw")
        canvas_main["highlightthickness"] = 0
        canvas_main.create_image(0, 0, anchor="nw", image=(self.ranking_main_bgm))
        if title:
            path_img_ranking_frame = "./photo/new/result_ranking_bg_frame1.png"
            self.img_ranking_frame = img_process.generate(path_img_ranking_frame, width, height - relative_height / 2)
            canvas_main.create_image(0, (relative_height / 2), anchor="nw", image=(self.img_ranking_frame))
        elif scan:
            if diff_bgi:
                canvas_main.create_text((0.94 * width / 2), (relative_height - head_size / 4), text=(language.GAME_RANK + "              " + language.GAME_PLAYER + "             " + language.PLAYER_PHONE + "              " + language.SCORE),
                  font=(
                 "STKaiti", int(0.015625 * width)),
                  fill="white")
            else:
                canvas_main.create_text((0.94 * width / 2), (relative_height - head_size / 4), text=(language.GAME_RANK + "              " + language.GAME_PLAYER + "             " + language.PLAYER_PHONE + "              " + language.SCORE + "              " + language.DATE),
                  font=(
                 "STKaiti", int(0.015625 * width)),
                  fill="white")
        else:
            if diff_bgi:
                canvas_main.create_text((0.94 * width / 2), (relative_height - head_size / 4), text=(" " + language.GAME_RANK + "              " + language.GAME_PLAYER + "                         " + "              " + language.SCORE),
                  font=(
                 "STKaiti", int(0.015625 * width)),
                  fill="white")
            else:
                canvas_main.create_text((0.94 * width / 2), (relative_height - head_size / 4), text=(" " + language.GAME_RANK + "              " + language.GAME_PLAYER + "                         " + "              " + language.SCORE + "              " + language.DATE),
                  font=(
                 "STKaiti", int(0.015625 * width)),
                  fill="white")
        canvas = Canvas(canvas_main, width=ranking_width, height=ranking_height, borderwidth=0)
        canvas["highlightthickness"] = 0
        canvas.place(x=fm_bgm_fm_size, y=(0 + relative_height), anchor="nw")
        canvas.create_image(0, 0, anchor="nw", image=(self.img_ranking_crop), tag="background")
        self.canvas_ranking = canvas
        scroll_width = 15
        vbar = tkinter.Scrollbar(canvas_main, orient=VERTICAL, borderwidth=0, bg="#66ffff")
        vbar.place(x=(width - scroll_width - fm_bgm_fm_size), y=(0 + relative_height), anchor="nw", height=ranking_height, width=scroll_width)
        vbar["highlightthickness"] = 0
        vbar.config(command=(self.custom_yview2))
        canvas.config(yscrollcommand=(vbar.set))
        self.sb_scroll = vbar
        if title:
            if diff_bgi:
                title_name = language.PLAY_RANKING_LIST + "(" + language.SCORE + ")"
            else:
                title_name = language.PLAY_RANKING_LIST + "(" + language.DATE + ")"
            path_img_ranking_title_btn = "./photo/new/ranking_list_head_frame.png"
            self.img_ranking_ranking_title_btn = img_process.generate(path_img_ranking_title_btn, width / 4, height / 6)
            canvas_title = Canvas(canvas_main, bg="black", width=title_width, height=title_height, borderwidth=0, highlightthickness=0)
            canvas_title.place(x=(width / 2), y=(relative_height / 2), anchor="center")
            canvas_title.create_image(0, 0, anchor="nw", image=(self.img_ranking_title))
            self.bt_game_level_title = Button_Canvas(canvas_title, 0, 0, title_width, title_height, title_name, no_frame_img=True,
              image_path=path_img_ranking_title_btn,
              fontsize=(int(0.015625 * width)),
              d_fill="white")
        self.list_tag = []
        self.row_max = -1
        self.row_min = 0
        self.display_nums = 10
        self.data = data
        self.data_size = len(data)
        self.page_nums = 2
        distance = self.page_nums * ranking_height / (self.display_nums + 1)
        self.row_size = distance
        self.page_size = int(self.display_nums / self.page_nums) * self.row_size
        bg_img_width = ranking_width * 9 / 10
        bg_img_height = self.row_size * 9 / 10
        self.row_1_bg_img = img_process.generate(row_1_bg_img_path, bg_img_width, bg_img_height)
        self.row_2_bg_img = img_process.generate(row_2_bg_img_path, bg_img_width, bg_img_height)
        self.row_3_bg_img = img_process.generate(row_3_bg_img_path, bg_img_width, bg_img_height)
        self.row_bg_img = img_process.generate(row_bg_img_path, bg_img_width, bg_img_height)
        for i in range(self.display_nums):
            if self.row_max < self.data_size - 1:
                self.row_max += 1
                tag = "row" + str(self.row_max)
                if diff_bgi:
                    if self.row_max == 0:
                        image = self.row_1_bg_img
                        rangking = "  "
                        img_tag = "row_1_bg_img"
                    else:
                        if self.row_max == 1:
                            image = self.row_2_bg_img
                            rangking = "  "
                            img_tag = "row_2_bg_img"
                        else:
                            if self.row_max == 2:
                                image = self.row_3_bg_img
                                rangking = "  "
                                img_tag = "row_3_bg_img"
                            else:
                                image = self.row_bg_img
                                rangking = "{:02d}".format(self.row_max + 1)
                                img_tag = "row_bg_img"
                else:
                    image = self.row_bg_img
                    rangking = "{:02d}".format(self.row_max + 1)
                    img_tag = "row_bg_img"
                self.canvas_ranking.create_image((ranking_width / 2), (distance * i + distance), anchor="center", image=(self.row_bg_img),
                  tag="row_bg_img")
                if self.row_max < 3:
                    self.canvas_ranking.create_image((ranking_width / 2), (distance * i + distance), anchor="center", image=image,
                      tag=img_tag)
                elif diff_bgi:
                    self.canvas_ranking.create_text((ranking_width / 2), (distance * i + distance), text=(rangking + "         " + data[self.row_max]),
                      font=(
                     "STKaiti", int(0.020833333333333332 * width)),
                      fill="white",
                      tags=tag)
                else:
                    self.canvas_ranking.create_text((ranking_width / 2), (distance * i + distance), text=(data[self.row_max]),
                      font=(
                     "STKaiti", int(0.015625 * width)),
                      fill="white",
                      tags=tag)
                self.list_tag.append(tag)

        width_canvas = canvas.winfo_width()
        canvas.config(scrollregion=(0, 0, width_canvas, 2 * ranking_height))
        self.width = width
        self.height = height

    def add_row(self, nums, direct=1):
        distance = self.row_size
        if direct:
            for i in range(nums):
                if self.row_max < self.data_size - 1:
                    self.row_max += 1
                    tag = "row" + str(self.row_max)
                    if self.diff_bgi:
                        if self.row_max < 3:
                            ranking = "  "
                            if self.row_max == 0:
                                self.canvas_ranking.itemconfig("row_1_bg_img", state="normal")
                            else:
                                if self.row_max == 1:
                                    self.canvas_ranking.itemconfig("row_2_bg_img", state="normal")
                                else:
                                    self.canvas_ranking.itemconfig("row_3_bg_img", state="normal")
                        else:
                            ranking = "{:02d}".format(self.row_max + 1)
                        self.canvas_ranking.create_text((self.ranking_width / 2), ((self.display_nums - nums + 1) * distance + distance * i), text=(ranking + "         " + self.data[self.row_max]),
                          font=(
                         "STKaiti", int(0.020833333333333332 * self.width)),
                          fill="white",
                          tags=tag)
                    else:
                        self.canvas_ranking.create_text((self.ranking_width / 2), ((self.display_nums - nums + 1) * distance + distance * i),
                          text=(self.data[self.row_max]),
                          font=(
                         "STKaiti", int(0.015625 * self.width)),
                          fill="white",
                          tags=tag)
                    self.list_tag.append(tag)
                else:
                    self.row_max += 1
                    tag = "row" + str(self.row_max)
                    self.canvas_ranking.create_text((self.ranking_width / 2), ((self.display_nums - nums + 1) * distance + distance * i),
                      text="",
                      font=(
                     "STKaiti", int(0.020833333333333332 * self.width)),
                      fill="white",
                      tags=tag)
                    self.list_tag.append(tag)

        else:
            for i in range(nums):
                if self.row_min > 0:
                    self.row_min -= 1
                    tag = "row" + str(self.row_min)
                    if self.diff_bgi:
                        if self.row_min < 3:
                            ranking = "  "
                            if self.row_min == 0:
                                self.canvas_ranking.itemconfig("row_1_bg_img", state="normal")
                            else:
                                if self.row_min == 1:
                                    self.canvas_ranking.itemconfig("row_2_bg_img", state="normal")
                                else:
                                    self.canvas_ranking.itemconfig("row_3_bg_img", state="normal")
                        else:
                            ranking = "{:02d}".format(self.row_min + 1)
                        self.canvas_ranking.create_text((self.ranking_width / 2), (distance * (nums - i)),
                          text=(ranking + "         " + self.data[self.row_min]),
                          font=(
                         "STKaiti", int(0.020833333333333332 * self.width)),
                          fill="white",
                          tags=tag)
                    else:
                        self.canvas_ranking.create_text((self.ranking_width / 2), (distance * (nums - i)),
                          text=(self.data[self.row_min]),
                          font=(
                         "STKaiti", int(0.015625 * self.width)),
                          fill="white",
                          tags=tag)
                    self.list_tag.insert(0, tag)
                else:
                    break

    def delete_row(self, nums, direct=1):
        if direct:
            for i in range(nums):
                self.canvas_ranking.delete(self.list_tag[i])

            self.list_tag = self.list_tag[nums[:None]]
            if self.row_min == 0:
                ranking = "  "
                self.canvas_ranking.itemconfig("row_1_bg_img", state="hidden")
                self.canvas_ranking.itemconfig("row_2_bg_img", state="hidden")
                self.canvas_ranking.itemconfig("row_3_bg_img", state="hidden")
            self.row_min += nums
        else:
            for i in range(nums):
                self.canvas_ranking.delete(self.list_tag[-(i + 1)])

            self.list_tag = self.list_tag[None[:nums]]
            self.row_max -= nums

    def move_row(self, nums, direct=1):
        distance = self.page_size
        if direct:
            for i in range(nums):
                coors = self.canvas_ranking.coords(self.list_tag[-(i + 1)])
                self.canvas_ranking.coords(self.list_tag[-(i + 1)], coors[0], coors[1] - distance)

        else:
            for i in range(nums):
                coors = self.canvas_ranking.coords(self.list_tag[i])
                self.canvas_ranking.coords(self.list_tag[i], coors[0], coors[1] + distance)

    def custom_yview2(self, *args, **kwargs):
        canvas = self.canvas_ranking
        (canvas.yview)(*args, **kwargs)
        x = canvas.canvasx(0)
        y = canvas.canvasy(0)
        canvas.coords("background", x, y)
        sb_video = self.sb_scroll
        cur_pos = sb_video.get()
        if self.data_size > self.display_nums:
            change_nums = int(self.display_nums / 2)
            if cur_pos[1] == 1:
                tmp_left = self.data_size - self.row_max - 1
                if tmp_left > 0:
                    self.move_row(change_nums)
                    self.delete_row(change_nums)
                    self.add_row(change_nums)
                    sb_video.set(0.45, 0.95)
                    sb_video.update()
            elif cur_pos[0] == 0:
                if self.row_min >= change_nums - 1:
                    self.move_row(change_nums, direct=0)
                    self.delete_row(change_nums, direct=0)
                    self.add_row(change_nums, direct=0)
                    sb_video.set(0.05, 0.55)
                    sb_video.update()

    def scroll_cb(self, *args):
        time_total = 1
        if time_total != 0:
            argc = len(args)
            sb_video = self.sb_scroll
            pages = 0.5 / time_total
            units = 0.2 / time_total
            cur_pos = sb_video.get()
            new_pos = 0
            if args[0] == "moveto":
                new_pos = float(args[1])
            else:
                if args[0] == "scroll":
                    if args[2] == "pages":
                        new_pos = cur_pos[0] + int(args[1]) * pages
                    else:
                        if args[2] == "units":
                            new_pos = cur_pos[0] + int(args[1]) * units
            sb_video.set(new_pos, new_pos + 0.5)

# okay decompiling /games/climb/climb_source_code/gui/gui_game_ranking_canvas.pyc
