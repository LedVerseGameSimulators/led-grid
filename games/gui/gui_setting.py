# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.14.4 (main, Apr  7 2026, 13:13:20) [Clang 17_iter__iter_ (clang-1700.6.4.2)]
# Embedded file name: gui_setting.py
import sys, threading, tkinter, time, traceback
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkinter.messagebox import OK
from loguru import logger
import encryption.yanqian as yanqian
from gui.gui_wall_light_position_setting import WallLightSetting
import gui.language as language
from gui2.gui_table_editor import TableEditor
from led import communication, position_convert
import shelve
import led.led_control as led_control
import gui2.gui_util as util
from functools import partial
from led.led_serial_thread import LedSerialThread, ScreenSerialThread
from model import setting
from model.setting import Color
led_num_one_team = 64

class Setting:
    LED_USE_COLOR = Color.GRAY
    LED_NO_USE_COLOR = (204, 179, 140)
    LED_NO_USE_COLOR_FORMAT = "#CCB38C"

    def wall_light_position_logic(self, start=1, size=0, direct='right'):
        out = []
        if direct == "right":
            for y in range(size):
                y += 1
                x = (y - (start - 1) + size) % size
                if x == 0:
                    x = size
                out.append(x)

        if direct == "left":
            for y in range(size):
                y += 1
                x = (size - (y - start) + 1) % size
                if x == 0:
                    x = size
                out.append(x)

        return out

    def wall_light_position_real(self, start=1, size=0, direct='right'):
        out = []
        if direct == "right":
            for x in range(size):
                x += 1
                y = (x + (start - 1)) % size
                if y == 0:
                    y = size
                out.append(y)

        if direct == "left":
            for x in range(size):
                x += 1
                y = (size - (x - 1) + start) % size
                if y == 0:
                    y = size
                out.append(y)

        return out

    def set_wall_light_layout_array(self, m, n):
        self.calcu_wall_position(m, n)
        standar_size = len(self.wall_light_table)
        self.wall_light_layout_real = []
        self.wall_light_layout_logic = []
        if standar_size > 0:
            self.wall_light_layout_real = self.wall_light_position_real(self.wall_start.get(), standar_size, self.wall_direct.get())
            self.wall_light_layout_logic = self.wall_light_position_logic(self.wall_start.get(), standar_size, self.wall_direct.get())
            try:
                list_data = []
                str_tmp = self.wall_posi_del.get()
                arr = str_tmp.split(",")
                for d in arr:
                    self.wall_light_layout_real.remove(int(d))
                    self.wall_light_layout_logic.remove(int(d))

            except:
                pass

    def __init__(self):
        self.dict_com_obj_thread = dict()
        self.wall_light_table = []
        self.read_parameter()
        self.read_sw_parameter()

    def read_sw_parameter(self):
        f = shelve.open("./setting/led_parameter")
        try:
            self.game_leval = IntVar()
            self.game_leval.set(f["game_leval_sw"])
        except:
            self.game_leval.set(1)

        try:
            self.leval_span = DoubleVar()
            self.leval_span.set(f["leval_span_sw"])
        except:
            self.leval_span.set(0.5)

        try:
            self.blue_hide_max_time = DoubleVar()
            self.blue_hide_max_time.set(f["blue_hide_max_time_sw"])
        except:
            self.blue_hide_max_time.set(15)

        try:
            self.hidden_show_time = DoubleVar()
            self.hidden_show_time.set(f["hidden_show_time"])
        except:
            self.hidden_show_time.set(5)

        try:
            self.hidn_tread_show_time = DoubleVar()
            self.hidn_tread_show_time.set(f["hidn_tread_show_time"])
        except:
            self.hidn_tread_show_time.set(3)

        try:
            self.game_result_show_time = IntVar()
            self.game_result_show_time.set(f["game_result_show_time"])
        except:
            self.game_result_show_time.set(6)

        try:
            self.hidden_prompt_score = IntVar()
            self.hidden_prompt_score.set(f["hidden_prompt_score"])
        except:
            self.hidden_prompt_score.set(10)

        try:
            self.hidden_prompt_breath_color = StringVar()
            self.hidden_prompt_breath_color.set(f["hidden_prompt_breath_color"])
        except:
            self.hidden_prompt_breath_color.set("#FAFA0A")

        try:
            self.game_pass = StringVar()
            self.game_pass.set(f["game_pass_sw"])
        except:
            self.game_pass.set("")

        try:
            self.player_num = IntVar()
            self.player_num.set(f["player_num_sw"])
        except:
            self.player_num.set("0")

        try:
            self.game_time = DoubleVar()
            self.game_time.set(f["game_time_sw"])
        except:
            self.game_time.set(1)

        try:
            self.game_name = StringVar()
            self.game_name.set(f["game_name_sw"])
        except:
            self.game_name.set("")

        try:
            self.life_value = IntVar()
            self.life_value.set(f["life_value_sw"])
        except:
            self.life_value.set(5)

        try:
            self.game_bg_audio = StringVar()
            self.game_bg_audio.set(f["game_bg_audio_sw"])
        except:
            self.game_bg_audio.set("")

        try:
            self.game_blood = StringVar()
            self.game_blood.set(f["game_blood_sw"])
        except:
            self.game_blood.set("")

        try:
            self.game_failure = StringVar()
            self.game_failure.set(f["game_failure_sw"])
        except:
            self.game_failure.set("")

        try:
            self.game_leval_editable = BooleanVar()
            self.game_leval_editable.set(f["game_leval_editable_sw"])
        except:
            self.game_leval_editable.set(False)

        try:
            self.game_scode = StringVar()
            self.game_scode.set(f["game_scode_sw"])
        except:
            self.game_scode.set("")

        try:
            self.game_start_video = StringVar()
            self.game_start_video.set(f["game_start_video_sw"])
        except:
            self.game_start_video.set("")

        try:
            self.game_time_editable = BooleanVar()
            self.game_time_editable.set(f["game_time_editable_sw"])
        except:
            self.game_time_editable.set(True)

        try:
            self.game_scode_divide_person = BooleanVar()
            self.game_scode_divide_person.set(f["game_scode_divide_person"])
        except:
            self.game_scode_divide_person.set(False)

        try:
            self.game_scode_divide_time = BooleanVar()
            self.game_scode_divide_time.set(f["game_scode_divide_time"])
        except:
            self.game_scode_divide_time.set(False)

        try:
            self.game_type_name = StringVar()
            self.game_type_name.set(f["game_type_name_sw"])
        except:
            self.game_type_name.set(language.GAME_TYPE_ONE)

        try:
            self.game_type_name2 = StringVar()
            self.game_type_name2.set(f["game_type_name2_sw"])
        except:
            self.game_type_name2.set(language.GAME_TYPE_TWO)

        try:
            self.game_type_name3 = StringVar()
            self.game_type_name3.set(f["game_type_name3_sw"])
        except:
            self.game_type_name3.set(language.GAME_TYPE_THREE)

        try:
            self.game_type_name4 = StringVar()
            self.game_type_name4.set(f["game_type_name4_sw"])
        except:
            self.game_type_name4.set(language.GAME_TYPE_THREE)

        try:
            self.game_type_video = StringVar()
            self.game_type_video.set(f["game_type_video_sw"])
        except:
            self.game_type_video.set("")

        try:
            self.game_type_video2 = StringVar()
            self.game_type_video2.set(f["game_type_video2_sw"])
        except:
            self.game_type_video2.set("")

        try:
            self.game_type_video3 = StringVar()
            self.game_type_video3.set(f["game_type_video3_sw"])
        except:
            self.game_type_video3.set("")

        try:
            self.game_type_video4 = StringVar()
            self.game_type_video4.set(f["game_type_video4_sw"])
        except:
            self.game_type_video4.set("")

        try:
            self.life_value_editable = BooleanVar()
            self.life_value_editable.set(f["life_value_editable_sw"])
        except:
            self.life_value_editable.set(False)

        try:
            self.player_num_editable = BooleanVar()
            self.player_num_editable.set(f["player_num_editable_sw"])
        except:
            self.player_num_editable.set(False)

        try:
            self.text_introduce2 = StringVar()
            self.text_introduce2.set(f["text_introduce2_sw"])
        except:
            self.text_introduce2.set("")

        try:
            self.text_introduce1 = StringVar()
            self.text_introduce1.set(f["text_introduce1_sw"])
        except:
            self.text_introduce1.set("")

        try:
            self.text_introduce3 = StringVar()
            self.text_introduce3.set(f["text_introduce3_sw"])
        except:
            self.text_introduce3.set("")

        try:
            self.text_introduce4 = StringVar()
            self.text_introduce4.set(f["text_introduce4_sw"])
        except:
            self.text_introduce4.set("")

        try:
            self.barcode_function = BooleanVar()
            self.barcode_function.set(f["barcode_function_sw"])
        except:
            self.barcode_function.set(False)

        try:
            self.game_idle_video = StringVar()
            self.game_idle_video.set(f["game_idle_video_sw"])
        except:
            self.game_idle_video.set("")

        try:
            self.idle_video_time_span = IntVar()
            self.idle_video_time_span.set(f["idle_video_time_span"])
        except:
            self.idle_video_time_span.set(1440)

        try:
            self.idle_video = StringVar()
            self.idle_video.set(f["idle_video_sw"])
        except:
            self.idle_video.set("")

        try:
            self.local_music = BooleanVar()
            self.local_music.set(f["local_music_sw"])
        except:
            self.local_music.set(True)

        f.close()

    def read_parameter(self):
        f = shelve.open("./setting/led_parameter")
        list_com = []
        try:
            self.value_width = StringVar()
            width = f.get("value_width")
            if width is None:
                self.value_width.set(26)
            else:
                self.value_width.set(width)
            self.value_high = StringVar()
            hight = f.get("value_high")
            if hight is None:
                self.value_high.set(16)
            else:
                self.value_high.set(hight)
            self.value_from = StringVar()
            value_from = f.get("value_from")
            if value_from is None:
                self.value_from.set(language.LEFT_UP)
            else:
                self.value_from.set(language.LIST_FROM[value_from])
            self.value_direction = StringVar()
            direction = f.get("value_direction")
            if direction is None:
                self.value_direction.set(language.RIGHT)
            else:
                self.value_direction.set(language.LIST_DIRECTION[direction])
            self.type = f.get("led_layout_type")
            self.list_com_name = f.get("list_com_name")
            self.list_com_info = f.get("list_com_info")
            self.list_wall_com_info = f.get("list_wall_com_info")
            self.list_screen_com_info = f.get("list_screen_com_info")
            self.wall_light_layout_real = f.get("wall_light_layout_real")
            self.wall_light_layout_logic = f.get("wall_light_layout_logic")
            self.wall_light_table = f.get("wall_light_table")
            self.floor_layout_coors_no_use = f.get("floor_layout_coors_no_use")
            self.wall_start = IntVar()
            start = f.get("wall_layout_start")
            if start is None:
                self.wall_start.set(1)
            else:
                self.wall_start.set(start)
            self.wall_direct = StringVar()
            direct = f.get("wall_layout_direct")
            if direct is None:
                self.wall_direct.set("right")
            else:
                self.wall_direct.set(direct)
            self.wall_posi_del = StringVar()
            posi_del = f.get("wall_layout_delete")
            if posi_del is None:
                self.wall_posi_del.set("")
            else:
                self.wall_posi_del.set(posi_del)
            self.light = BooleanVar()
            light = f.get("wall_light")
            if light is None:
                self.light.set(False)
            else:
                self.light.set(light)
            self.screen = BooleanVar()
            screen = f.get("screen_light")
            if screen is None:
                self.screen.set(False)
            else:
                self.screen.set(screen)
            self.ip_address = StringVar()
            ip_address = f.get("ip_address")
            if ip_address is None:
                self.ip_address.set("localhost")
            else:
                self.ip_address.set(ip_address)
            self.local_ip_address = StringVar()
            ip_address = f.get("local_ip_address")
            if ip_address is None:
                self.local_ip_address.set("127_iter__iter_.1")
            else:
                self.local_ip_address.set(ip_address)
            self.local_ip_port = StringVar()
            ip_address = f.get("local_ip_port")
            if ip_address is None:
                self.local_ip_port.set("8080")
            else:
                self.local_ip_port.set(ip_address)
            self.corner_line_start = IntVar()
            corner_line_start = f.get("corner_line_start")
            if corner_line_start is None:
                self.corner_line_start.set(0)
            else:
                self.corner_line_start.set(corner_line_start)
            if self.list_com_name is None or len(self.list_com_name) == 0:
                self.list_com_name = []
            if self.list_com_info is None or len(self.list_com_info) == 0:
                self.list_com_info = []
            if self.list_wall_com_info is None or len(self.list_wall_com_info) == 0:
                self.list_wall_com_info = []
            if self.list_screen_com_info is None or len(self.list_screen_com_info) == 0:
                self.list_screen_com_info = []
            if self.wall_light_table is None or len(self.wall_light_table) == 0:
                self.set_wall_light_layout_array(int(self.value_high.get()), int(self.value_width.get()))
            if self.floor_layout_coors_no_use is None:
                self.floor_layout_coors_no_use = []
        except:
            self.value_width = StringVar()
            self.value_width.set(26)
            self.value_high = StringVar()
            self.value_high.set(16)
            self.value_from = StringVar()
            self.value_from.set(language.LEFT_UP)
            self.value_direction = StringVar()
            self.value_direction.set(language.RIGHT)
            self.list_com_name = []
            self.list_com_info = []
            self.type = position_convert.LEFT_TOP_RIGHT
            list_com = communication.Communication.get_com_list()
            for com in list_com:
                self.list_com_name.append(com.name)
                self.list_com_info.append([com.name, 0, 0, "floor_light"])

            self.list_wall_com_info = []
            self.list_screen_com_info = []
            self.wall_start = IntVar()
            self.wall_start.set(1)
            self.wall_direct = StringVar()
            self.wall_direct.set("right")
            self.wall_posi_del = StringVar()
            self.wall_posi_del.set("")
            self.light.set(False)
            self.screen.set(False)
            self.ip_address.set("localhost")
            self.game_leval.set(1)
            self.corner_line_start.set(0)

        f.close()

    def led_from_string_to_int(self, str_from):
        ret_int_from = 0
        for index, from_ in enumerate(language.LIST_FROM):
            if from_ == str_from:
                ret_int_from = index

        return ret_int_from

    def led_direction_string_to_int(self, str_direction):
        ret_int_direction = 0
        for index, str_ in enumerate(language.LIST_DIRECTION):
            if str_ == str_direction:
                ret_int_direction = index

        return ret_int_direction

    def save_sw_parameter_main_input(self):
        f = shelve.open("./setting/led_parameter")
        f["game_leval_sw"] = self.game_leval.get()
        f["player_num_sw"] = self.player_num.get()
        f["game_time_sw"] = self.game_time.get()
        f["life_value_sw"] = self.life_value.get()
        f.close()

    def save_sw_parameter(self):
        f = shelve.open("./setting/led_parameter")
        f["game_leval_sw"] = self.game_leval.get()
        f["blue_hide_max_time_sw"] = self.blue_hide_max_time.get()
        f["hidden_show_time"] = self.hidden_show_time.get()
        f["hidn_tread_show_time"] = self.hidn_tread_show_time.get()
        f["game_result_show_time"] = self.game_result_show_time.get()
        f["hidden_prompt_score"] = self.hidden_prompt_score.get()
        f["hidden_prompt_breath_color"] = self.hidden_prompt_breath_color.get()
        f["leval_span_sw"] = self.leval_span.get()
        f["game_pass_sw"] = self.game_pass.get()
        f["player_num_sw"] = self.player_num.get()
        f["game_time_sw"] = self.game_time.get()
        f["game_name_sw"] = self.game_name.get()
        f["life_value_sw"] = self.life_value.get()
        f["game_bg_audio_sw"] = self.game_bg_audio.get()
        f["game_blood_sw"] = self.game_blood.get()
        f["game_failure_sw"] = self.game_failure.get()
        f["game_leval_editable_sw"] = self.game_leval_editable.get()
        f["game_scode_sw"] = self.game_scode.get()
        f["game_start_video_sw"] = self.game_start_video.get()
        f["game_time_editable_sw"] = self.game_time_editable.get()
        f["game_type_name_sw"] = self.game_type_name.get()
        f["game_type_name2_sw"] = self.game_type_name2.get()
        f["game_type_name3_sw"] = self.game_type_name3.get()
        f["game_type_name4_sw"] = self.game_type_name4.get()
        f["game_type_video_sw"] = self.game_type_video.get()
        f["game_type_video2_sw"] = self.game_type_video2.get()
        f["game_type_video3_sw"] = self.game_type_video3.get()
        f["game_type_video4_sw"] = self.game_type_video4.get()
        f["life_value_editable_sw"] = self.life_value_editable.get()
        f["player_num_editable_sw"] = self.player_num_editable.get()
        f["game_scode_divide_person"] = self.game_scode_divide_person.get()
        f["game_scode_divide_time"] = self.game_scode_divide_time.get()
        f["game_idle_video_sw"] = self.game_idle_video.get()
        f["idle_video_sw"] = self.idle_video.get()
        f["idle_video_time_span"] = self.idle_video_time_span.get()
        f["local_music_sw"] = self.local_music.get()
        text = self.text_introduce_widget2.get("1", END).strip()
        f["text_introduce2_sw"] = text
        self.text_introduce2.set(text)
        text = self.text_introduce_widget1.get("1", END).strip()
        f["text_introduce1_sw"] = text
        self.text_introduce1.set(text)
        text = self.text_introduce_widget3.get("1", END).strip()
        f["text_introduce3_sw"] = text
        self.text_introduce3.set(text)
        text = self.text_introduce_widget4.get("1", END).strip()
        f["text_introduce4_sw"] = text
        self.text_introduce4.set(text)
        f["barcode_function_sw"] = self.barcode_function.get()
        f.close()

    def save_parameter(self):
        f = shelve.open("./setting/led_parameter")
        f["value_width"] = self.value_width.get()
        f["value_high"] = self.value_high.get()
        tmp = self.value_from.get()
        f["value_from"] = self.led_from_string_to_int(self.value_from.get())
        f["value_direction"] = self.led_direction_string_to_int(self.value_direction.get())
        f["led_layout_type"] = self.type
        f["list_com_name"] = self.list_com_name
        f["list_com_info"] = self.list_com_info
        f["list_wall_com_info"] = self.list_wall_com_info
        f["list_screen_com_info"] = self.list_screen_com_info
        f["wall_layout_start"] = self.wall_start.get()
        f["wall_layout_direct"] = self.wall_direct.get()
        f["wall_layout_delete"] = self.wall_posi_del.get()
        f["wall_light_layout_real"] = self.wall_light_layout_real
        f["wall_light_layout_logic"] = self.wall_light_layout_logic
        f["floor_layout_coors_no_use"] = self.floor_layout_coors_no_use
        f["wall_light_table"] = self.wall_light_table
        f["wall_light"] = self.light.get()
        f["screen_light"] = self.screen.get()
        f["ip_address"] = self.ip_address.get()
        f["local_ip_address"] = self.local_ip_address.get()
        f["local_ip_port"] = self.local_ip_port.get()
        f["game_leval"] = self.game_leval.get()
        f["corner_line_start"] = self.corner_line_start.get()
        f.close()

    def group_member_and_com_setting(self):
        row_start = 5
        col_start = 0
        self.lable_list = []
        for i in range(self.value_group_nums):
            exec("lable" + str(i) + "=ttk.Lable(self.master,text=" + str(i) + ")")
            eval("lable" + str(i)).grid(row=(row_start + i), col=0)
            self.lable_list.append(eval("lable" + str(i)))
            com_name = StringVar()
            en_group = ttk.Entry((self.master), textvariable=(self.value_group_nums))
            en_group.grid(row=row_start, col=1, columnspan=2)

    def get_type(self):
        type = position_convert.LEFT_TOP_RIGHT
        if self.value_from.get() == language.LEFT_UP and self.value_direction.get() == language.RIGHT:
            type = position_convert.LEFT_TOP_RIGHT
        else:
            if self.value_from.get() == language.LEFT_UP and self.value_direction.get() == language.DOWN:
                type = position_convert.LEFT_TOP_DOWN
            else:
                if self.value_from.get() == language.RIGHT_UP and self.value_direction.get() == language.LEFT:
                    type = position_convert.RIGHT_TOP_LEFT
                else:
                    if self.value_from.get() == language.RIGHT_UP and self.value_direction.get() == language.DOWN:
                        type = position_convert.RIGHT_TOP_DOWN
                    else:
                        if self.value_from.get() == language.LEFT_DOWN and self.value_direction.get() == language.RIGHT:
                            type = position_convert.LEFT_DOWN_RIGHT
                        else:
                            if self.value_from.get() == language.LEFT_DOWN and self.value_direction.get() == language.UP:
                                type = position_convert.LEFT_DOWN_UP
                            else:
                                if self.value_from.get() == language.RIGHT_DOWN and self.value_direction.get() == language.LEFT:
                                    type = position_convert.RIGHT_DOWN_LEFT
                                else:
                                    if self.value_from.get() == language.RIGHT_DOWN and self.value_direction.get() == language.UP:
                                        type = position_convert.RIGHT_DOWN_UP
                                    else:
                                        logger.debug("in btn_comform error")
        return type

    def btn_comform(self, fm_layout_setting):
        try:
            self.type = self.get_type()
            row = int(self.value_high.get())
            col = int(self.value_width.get())
            size = row * col
            self.list_com_info = []
            self.list_com_name = []
            self.list_wall_com_info = []
            self.list_screen_com_info = []
            for com_info in self.list_controler_var:
                if int(com_info[1].get()) >= 1:
                    if int(com_info[2].get()) <= size:
                        if com_info[3].get() == "floor_light":
                            self.list_com_info.append([com_info[0].get(), com_info[1].get(), com_info[2].get(), com_info[3].get()])
                            self.list_com_name.append(com_info[0].get())
                    else:
                        if com_info[3].get() == "wall_light":
                            self.list_wall_com_info.append([com_info[0].get(), com_info[1].get(), com_info[2].get(), com_info[3].get()])
                    if com_info[3].get() == "screen_light":
                        self.list_screen_com_info.append([com_info[0].get(), com_info[1].get(), com_info[2].get(), com_info[3].get()])

            for com_info in self.list_com_info:
                if com_info[1] is int and com_info[2] is int and com_info[1] > 0 and com_info[1] <= size and com_info[2] > 0 and com_info[2] <= size:
                    self.dict_com_info[com_info[0]] = [
                     com_info[1], com_info[2]]

            self.set_wall_light_layout_array(row, col)
            if self.last_size != (row, col):
                self.floor_layout_coors_no_use = []
                self.last_size = (
                 row, col)
                self.wall_posi_del.set("")
                self.last_light = self.light.get()
            if self.last_light != self.light.get():
                self.wall_posi_del.set("")
                self.last_light = self.light.get()
            self.save_parameter()
            self.fm_layout_setting_led_table.pack_forget()
            self.fm_layout_setting_led_table = ttk.Frame(fm_layout_setting)
            self.fm_layout_setting_led_table.pack(side=LEFT)
            self.init_led_no_use_table(self.fm_layout_setting_led_table, row, col)
        except:
            logger.error("soft setting update", traceback.format_exc())

    def get_director(self, position=None):
        if position == language.LEFT_UP:
            return [
             language.RIGHT, language.DOWN]
        if position == language.RIGHT_UP:
            return [
             language.LEFT, language.DOWN]
        if position == language.LEFT_DOWN:
            return [
             language.RIGHT, language.UP]
        return [language.LEFT, language.UP]

    def choose_(self, event):
        return

    def choose(self, event, com_from, com_direction):
        value_from = com_from.get()
        list_direction = self.get_director(value_from)
        com_direction["values"] = list_direction
        com_direction.set(list_direction[0])

    def com_change_prompt(self, frame_serial, last_list_com_scan, cur_list_com_name_scan, last_list_com_display, last_list_com_info):
        com_name_add_list = []
        com_name_delete_list = []
        com_name_add_list_display = []
        com_name_delete_list_display = []
        for cur_com_name in cur_list_com_name_scan:
            if cur_com_name not in last_list_com_scan:
                com_name_add_list.append(cur_com_name)

        for last_com_name in last_list_com_scan:
            if last_com_name not in cur_list_com_name_scan:
                com_name_delete_list.append(last_com_name)

        for com_name_add in com_name_add_list:
            if com_name_add not in last_list_com_display:
                com_name_add_list_display.append(com_name_add)

        for com_name_delete in com_name_delete_list:
            if com_name_delete in last_list_com_display:
                com_name_delete_list_display.append(com_name_delete)

        if len(com_name_add_list_display) > 0:
            ret = messagebox.askokcancel((language.FIND_NEW_SERIAL), (language.CHECK_ADD_NEW_SERIAL + ":\n" + str(com_name_add_list_display)),
              parent=(self.father_root))
            if ret:
                self.display_new_serial(frame_serial, com_name_add_list_display)
        if len(com_name_delete_list_display) > 0:
            ret = messagebox.askokcancel((language.FIND_NO_SERIAL), (language.CHECK_DELETE_SERIAL + ":\n" + str(com_name_delete_list_display)),
              parent=(self.father_root))
            if ret:
                self.display_delete_serial(com_name_delete_list_display, last_list_com_info)

    def btn_hardware_scan_new(self, frame_serial):
        cur_list_com_name_scan = led_control.get_com_name_list()
        last_list_com_display = []
        for com_info in self.list_controler_var:
            last_list_com_display.append(com_info[0].get())

        self.com_change_prompt(frame_serial, self.last_list_com_scan, cur_list_com_name_scan, last_list_com_display, self.list_controler_var)
        self.last_list_com_scan = cur_list_com_name_scan

    def on_combobox_select(self, com_value_var, fm_hardware_content_i, list_controller_var):
        selected_item = com_value_var.get()
        if selected_item == "cancel":
            for com_info in list_controller_var.copy():
                if com_info[4] == fm_hardware_content_i:
                    list_controller_var.remove(com_info)
                    print(com_info[1].get())

            fm_hardware_content_i.pack_forget()

    def serial_com_test_screen(self, root, com_name, led_start_var, led_end_var, text_var):
        com_obj = communication.Communication(com_name, 115200, 0.5)
        if com_obj.main_engine is not None and com_obj.main_engine.is_open:
            try:
                led_nums = int(led_end_var.get()) - int(led_start_var.get()) + 1
                if led_nums <= 0:
                    led_nums = 1
                if led_nums > 0:
                    array_com_protocal = [
                     255, 1, 1, 1, 3, 
                     85]
                    address_idx = 1
                    num_text_idx = 2
                    verify_code_idx = 4
                    color_idx = 3
                    last_time = time.time()
                    switch_color = False
                    while text_var.get() == language.STOP:
                        threading.sleep(0.1)
                        current_time = time.time()
                        time_pass = current_time - last_time
                        index = round(time_pass / 0.5) % 3
                        if index == 0:
                            array_com_protocal[color_idx] = 2
                        else:
                            if index == 1:
                                array_com_protocal[color_idx] = 3
                            else:
                                array_com_protocal[color_idx] = 4
                        for i in range(led_nums):
                            array_com_protocal[address_idx] = i + 1
                            array_com_protocal[num_text_idx] = i + 1
                            array_com_protocal[verify_code_idx] = 2 * i + 2 + array_com_protocal[color_idx]
                            com_obj.Send_data(array_com_protocal)

                        root.update()

                    com_obj.main_engine.close()
            except:
                if com_obj is not None and com_obj.main_engine is not None:
                    if com_obj.main_engine.is_open:
                        text_var.set(language.TEST)
                        com_obj.main_engine.close()

        else:
            text_var.set(language.TEST)
            messagebox.showerror((language.SERIAL), (com_name + language.SERIAL_OPEN_FAIL), parent=(self.father_root))

    def serial_com_test_led(self, root, com_name, led_start_var, led_end_var, text_var):
        read_size = 1000
        com_obj = communication.Communication(com_name, 115200, 0.5)
        if com_obj.main_engine is not None and com_obj.main_engine.is_open:
            read_buffer = com_obj.main_engine.read(read_size)
            try:
                index1_of_fc = read_buffer.index(252)
                index2_of_fc = read_buffer[(index1_of_fc + 1)[:None]].index(252)
                led_nums = index2_of_fc - 1
                led_end_var.set(led_nums + int(led_start_var.get()) - 1)
                if led_nums > 0:
                    array_com_protocal = [
                     255, 255]
                    for i in range(led_nums):
                        array_com_protocal.append(171)
                        array_com_protocal.append(171)
                        array_com_protocal.append(171)

                    array_com_protocal[2] = 0
                    array_com_protocal[3] = 0
                    array_com_protocal[4] = 254
                    array_com_protocal[-3] = 254
                    array_com_protocal[-2] = 0
                    array_com_protocal[-1] = 0
                    array_com_protocal_black = [
                     255, 255]
                    for i in range(led_nums):
                        for j in range(3):
                            array_com_protocal_black.append(0)

                    com_obj.Send_data(array_com_protocal)
                    last_time = time.time()
                    switch_color = False
                    while text_var.get() == language.STOP:
                        threading.sleep(0.2)
                        current_time = time.time()
                        time_pass = current_time - last_time
                        if time_pass > 1:
                            switch_color = not switch_color
                            last_time = current_time
                            if switch_color:
                                com_obj.Send_data(array_com_protocal_black)
                            else:
                                com_obj.Send_data(array_com_protocal)
                        root.update()

                    com_obj.Send_data(array_com_protocal_black)
                    com_obj.main_engine.close()
            except:
                if com_obj is not None and com_obj.main_engine is not None:
                    if com_obj.main_engine.is_open:
                        text_var.set(language.TEST)
                        com_obj.main_engine.close()

        else:
            text_var.set(language.TEST)
            messagebox.showerror((language.SERIAL), (com_name + language.SERIAL_OPEN_FAIL), parent=(self.father_root))

    def get_com_num(self, com_info_str):
        try:
            idx_com_name_start = com_info_str.index("(")
            idx_com_name_end = com_info_str.index(")")
            com_name = com_info_str[(idx_com_name_start + 1)[:idx_com_name_end]]
            return com_name
        except:
            logger.debug("get_com_num exception")
            return com_info_str

    def serial_com_test(self, root, com_name, led_start_var, led_end_var, text_var, led_type):
        led_type = led_type.get()
        com_name = com_name.get()
        com_name = self.get_com_num(com_name)
        if text_var.get() == language.TEST:
            text_var.set(language.STOP)
            if led_type == setting.Setting.FLOOR_LIGHT or led_type == setting.Setting.WALL_LIGHT:
                thread_led = LedSerialThread(root, com_name, led_start_var, led_end_var, text_var)
                thread_led.start()
                self.dict_com_obj_thread[com_name] = thread_led
            else:
                thread_led = ScreenSerialThread(root, com_name, led_start_var, led_end_var, text_var)
                thread_led.start()
                self.dict_com_obj_thread[com_name] = thread_led
        else:
            text_var.set(language.TEST)

    def display_delete_serial(self, list_com_name, list_controller_var):
        for com_info in list_controller_var.copy():
            if com_info[0].get() in list_com_name:
                com_info[4].pack_forget()
                list_controller_var.remove(com_info)

    def display_new_serial(self, frame_serial, list_com_name):
        i = 1
        for str_com in list_com_name:
            fm_hardware_content_i = ttk.Frame(frame_serial)
            fm_hardware_content_i.pack(side=TOP, fill=BOTH, expand=YES)
            value_com = StringVar()
            value_com.set(str_com)
            len_com_name = len(str_com)
            tmp_combobox = ttk.Combobox(fm_hardware_content_i, width=len_com_name, state="readonly",
              textvariable=value_com,
              values=list_com_name)
            tmp_combobox.pack(side=LEFT)
            ttk.Label(fm_hardware_content_i, text=(language.START_FROM)).pack(side=LEFT)
            value_com_pst_start = StringVar()
            value_com_pst_start.set(i * led_num_one_team - led_num_one_team + 1)
            ttk.Entry(fm_hardware_content_i, textvariable=value_com_pst_start, width=6).pack(side=LEFT)
            ttk.Label(fm_hardware_content_i, text=(language.LED_NUMS)).pack(side=LEFT)
            value_com_pst_end = StringVar()
            value_com_pst_end.set(i * led_num_one_team)
            ttk.Entry(fm_hardware_content_i, textvariable=value_com_pst_end, width=6).pack(side=LEFT)
            var_com_type = StringVar()
            ttk.Label(fm_hardware_content_i, text=(language.TYPE)).pack(side=LEFT)
            var_com_type.set("floor_light")
            t = ttk.Combobox(fm_hardware_content_i, textvariable=var_com_type, values=[
             "floor_light", "wall_light", "screen_light"],
              width=12)
            t.pack(side=LEFT)
            text_var = StringVar()
            text_var.set(language.TEST)
            ttk.Button(fm_hardware_content_i, textvariable=text_var, command=(partial(self.serial_com_test, self.father_root, value_com, value_com_pst_start, value_com_pst_end, text_var, var_com_type))).pack(side=LEFT)
            ttk.Button(fm_hardware_content_i, text=(language.DELETE), command=(partial(self.delete_com, fm_hardware_content_i)),
              width=4).pack(side=LEFT)
            list_com_i_info = [
             value_com, value_com_pst_start, value_com_pst_end, 
             var_com_type, 
             fm_hardware_content_i, 
             text_var]
            self.list_controler_var.append(list_com_i_info)
            i += 1

    def btn_hardware_scan(self):
        led_control.close_com()
        self.fm_hardware_content.destroy()
        self.fm_hardware_content = None
        fm_hardware = self.fm_hardware
        self.fm_hardware_content = ttk.Frame(fm_hardware)
        self.fm_hardware_content.pack()
        list_com_name = led_control.get_com_name_list()
        i = 1
        self.list_controler_var = []
        for str_com in list_com_name:
            fm_hardware_content_i = ttk.Frame(self.fm_hardware_content)
            fm_hardware_content_i.pack(side=TOP, fill=BOTH, expand=YES)
            ttk.Label(fm_hardware_content_i, text=(language.SERIAL + str(i))).pack(side=LEFT)
            value_com = StringVar()
            value_com.set(str_com)
            ttk.Combobox(fm_hardware_content_i, state="readonly", textvariable=value_com, values=list_com_name).pack(side=LEFT)
            ttk.Label(fm_hardware_content_i, text=(language.START_FROM)).pack(side=LEFT)
            value_com_pst_start = StringVar()
            value_com_pst_start.set(i * led_num_one_team - led_num_one_team + 1)
            ttk.Entry(fm_hardware_content_i, textvariable=value_com_pst_start).pack(side=LEFT)
            ttk.Label(fm_hardware_content_i, text=(language.END_IN)).pack(side=LEFT)
            value_com_pst_end = StringVar()
            value_com_pst_end.set(i * led_num_one_team)
            ttk.Entry(fm_hardware_content_i, textvariable=value_com_pst_end).pack(side=LEFT)
            var_com_type = StringVar()
            ttk.Label(fm_hardware_content_i, text=(language.TYPE)).pack(side=LEFT)
            var_com_type.set("floor_light")
            t = ttk.Combobox(fm_hardware_content_i, textvariable=var_com_type, values=[
             "floor_light", "wall_light", "screen_light"])
            t.pack(side=LEFT)
            list_com_i_info = [value_com, value_com_pst_start, value_com_pst_end, var_com_type]
            self.list_controler_var.append(list_com_i_info)
            i += 1

        self.master.update()

    def but_callback(self, event, x):
        print(x)

    def author(self):
        return

    def handler_adaptor(self, fun, **kwds):
        """事件处理函数的适配器，相当于中介，那个event是从那里来的呢，我也纳闷，这也许就是python的伟大之处吧"""
        return (lambda event, fun=fun, kwds=kwds: fun(event, **kwds))

    def delete_com(self, widget_frame):
        for com_info in self.list_controler_var.copy():
            if com_info[4] == widget_frame:
                self.list_controler_var.remove(com_info)

        widget_frame.pack_forget()

    def dyna_display_com_widget(self, list_com):
        i = 1
        for str_com in list_com:
            fm_hardware_content_i = ttk.Frame(self.fm_hardware_content)
            fm_hardware_content_i.pack(side=TOP, fill=BOTH, expand=YES)
            value_com = StringVar()
            value_com.set(list_com[i - 1][0])
            len_com_name = len(list_com[i - 1][0])
            tmp_combobox = ttk.Combobox(fm_hardware_content_i, width=len_com_name, state="readonly",
              textvariable=value_com,
              values=(self.list_com_name))
            tmp_combobox.pack(side=LEFT)
            ttk.Label(fm_hardware_content_i, text=(language.START_FROM)).pack(side=LEFT, padx=5)
            value_com_pst_start = StringVar()
            if list_com[i - 1][1] is not None:
                if list_com[i - 1][1] != "":
                    value_com_pst_start.set(int(list_com[i - 1][1]))
            t = ttk.Entry(fm_hardware_content_i, textvariable=value_com_pst_start, width=6)
            t.pack(side=LEFT)
            ttk.Label(fm_hardware_content_i, text=(language.LED_NUMS)).pack(side=LEFT, padx=5)
            value_com_pst_end = StringVar()
            if list_com[i - 1][2] is not None:
                if list_com[i - 1][2] != "":
                    value_com_pst_end.set(int(list_com[i - 1][2]))
            t = ttk.Entry(fm_hardware_content_i, textvariable=value_com_pst_end, width=6)
            t.pack(side=LEFT)
            var_com_type = StringVar()
            var_com_type.set(list_com[i - 1][3])
            ttk.Label(fm_hardware_content_i, text=(language.TYPE)).pack(side=LEFT)
            t = ttk.Combobox(fm_hardware_content_i, textvariable=var_com_type, values=[
             "floor_light", "wall_light", "screen_light"],
              width=12)
            t.pack(side=LEFT)
            text_var = StringVar()
            text_var.set(language.TEST)
            ttk.Button(fm_hardware_content_i, textvariable=text_var, command=(partial(self.serial_com_test, self.father_root, value_com, value_com_pst_start, value_com_pst_end, text_var, var_com_type))).pack(side=LEFT)
            ttk.Button(fm_hardware_content_i, text=(language.DELETE), command=(partial(self.delete_com, fm_hardware_content_i)), width=4).pack(side=LEFT)
            list_com_i_info = [value_com, value_com_pst_start, value_com_pst_end, var_com_type, fm_hardware_content_i, 
             text_var]
            self.list_controler_var.append(list_com_i_info)
            i += 1

    def calcu_wall_position_old(self, m, n):
        row_wall = 1
        col_wall = 4
        self.wall_light_table = []
        wall_light_table = self.wall_light_table
        light_total_num = int((2 * m + 2 * n - 4) / 3)
        for i in range(light_total_num):
            wall_light_table.append([row_wall - 1, col_wall - 1])
            if row_wall == 1:
                col_wall = col_wall + 3
                if col_wall > 1 + n:
                    col_wall = n + 2
                    row_wall = 3 - n % 3 + 2
                    continue
            if col_wall == n + 2:
                row_wall = row_wall + 3
                if row_wall > 1 + m:
                    row_wall = m + 2
                    col_wall = 1 + n - (3 - (n + m - 1) % 3)
                    continue
            if row_wall == m + 2:
                col_wall = col_wall - 3
                if col_wall < 2:
                    col_wall = 1
                    row_wall = 1 + m - (3 - (2 * n + m - 2) % 3)
                    continue
                if col_wall == 1:
                    row_wall = row_wall - 3
                if row_wall < 1:
                    break

    def calcu_wall_position(self, m, n):
        if n >= 3:
            row_wall = 1
            col_wall = 4
        else:
            row_wall = 2 - n % 3 + 2
            col_wall = n + 2
        if m * n == 1:
            self.wall_light_table = [
             [
              0, 1]]
            return
        self.wall_light_table = []
        wall_light_table = self.wall_light_table
        light_total_num = int((2 * m + 2 * n) / 3)
        for i in range(light_total_num):
            wall_light_table.append([row_wall - 1, col_wall - 1])
            if row_wall == 1:
                col_wall = col_wall + 3
                if col_wall > 1 + n:
                    col_wall = n + 2
                    row_wall = 2 + (2 - n % 3)
                    if row_wall >= m + 2:
                        row_wall = m + 2
                        col_wall = n - 1 + (n % 3 + m)
                        continue
            if col_wall == n + 2:
                row_wall = row_wall + 3
                if row_wall > 1 + m:
                    row_wall = m + 2
                    col_wall = 1 + n - (2 - (n + m) % 3)
                    if col_wall < 2:
                        col_wall = 1
                        row_wall = 1 + m - (2 - (2 * n + m) % 3)
                        continue
            if row_wall == m + 2:
                col_wall = col_wall - 3
                if col_wall < 2:
                    col_wall = 1
                    row_wall = 1 + m - (2 - (2 * n + m) % 3)
                    if row_wall > 1:
                        continue
                if col_wall == 1:
                    row_wall = row_wall - 3
                if row_wall < 1:
                    break

    def draw_wall_position(self, canvas, m, n):
        self.calcu_wall_position(m, n)
        x = 1
        for coors in self.wall_light_table:
            util.write_text_in_rectangle(canvas, coors, n + 2, m + 2, str(x))
            x += 1

    def draw_table_led_position(self, table_editor, table_rect, wall_light=False):
        col = len(table_rect[0])
        row = len(table_rect)
        if wall_light:
            for i in range(row):
                for j in range(col):
                    table_editor.write_text_in_table_cell((i + 1, j + 1), table_rect[i][j])

        else:
            for i in range(row):
                for j in range(col):
                    table_editor.write_text_in_table_cell((i, j), table_rect[i][j])

    def draw_table_canvas(self, fm_canvas, table_row, table_col):
        rect_table = [[0] * (table_col - 2) for _ in range(table_row - 2)]
        side_ = 25
        width = table_col * side_
        high = table_row * side_
        border = 1
        size = (width + border * table_col + border, high + border * table_row + border)
        canvas = Canvas(fm_canvas, width=(size[0]), height=(size[1]), background="white")
        canvas.pack()
        util.draw_rect_in_canvas(canvas, table_col, table_row)
        position_convert.record_led_arr_position_to_rect(self.type, rect_table)
        self.draw_table_led_position(canvas, rect_table)
        self.draw_wall_position(canvas, table_row - 2, table_col - 2)

    def wall_setting(self):
        WallLightSetting(self)
        print("after WallLightSetting")

    def check_click(self, value):
        if self.screen.get():
            self.light.set(True)

    def display_wall_setting(self):
        str_tmp = language.WALL_LAYOUT + "\n" + language.WALL_LAYOUT_START + ":" + str(self.wall_start.get()) + "\n" + language.WALL_LAYOUT_DIRECTION + ":" + self.wall_direct.get() + "\n" + language.WALL_LAYOUT_DELETE + ":" + self.wall_posi_del.get()
        self.wall_setting_text.set(str_tmp)
        self.set_wall_light_layout_array(int(self.value_high.get()), int(self.value_width.get()))

    def sw_checkbutton_click(self):
        print("sw_checkbutton_click")

    def sw_setting_conform(self):
        self.save_sw_parameter()

    def file_select(self, entry_var):
        file_path = filedialog.askopenfilename(parent=(self.parent_root), filetypes=[('Audio Files', '.mp3'), ('Video Files', '.mp4'), ('Game Files', '.led')], title=(language.OPEN_FILE))
        entry_var.set(file_path)

    def software_setting(self, parent_root, tab2, parent=None):
        self.read_sw_parameter()
        self.parent_root = parent_root
        labelframe = ttk.LabelFrame(tab2, text=(language.MAIN_WINDOW_SETTING))
        labelframe.pack(fill=BOTH, expand=YES)
        row_idx = 0
        col_idx = 0
        entry_width = 10
        ttk.Label(labelframe, text=(language.GAME_LIFE + language.COLON)).grid(row=row_idx, column=col_idx)
        ttk.Entry(labelframe, textvariable=(self.life_value), width=entry_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Checkbutton(labelframe, text=(language.MAIN_WINDOW_EDIT), variable=(self.life_value_editable), command=(self.sw_checkbutton_click)).grid(row=row_idx, column=(col_idx + 2))
        col_idx = col_idx + 4
        row_idx = 0
        ttk.Label(labelframe, text=(language.GAME_TIME + language.COLON)).grid(row=row_idx, column=col_idx)
        ttk.Entry(labelframe, textvariable=(self.game_time), width=entry_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Checkbutton(labelframe, text=(language.MAIN_WINDOW_EDIT), variable=(self.game_time_editable), command=(self.sw_checkbutton_click)).grid(row=row_idx, column=(col_idx + 2))
        col_idx = 0
        row_idx = 1
        ttk.Label(labelframe, text=(language.GAME_LEVAL + language.COLON)).grid(row=row_idx, column=col_idx)
        ttk.Entry(labelframe, textvariable=(self.game_leval), width=entry_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Checkbutton(labelframe, text=(language.MAIN_WINDOW_EDIT), variable=(self.game_leval_editable), command=(self.sw_checkbutton_click)).grid(row=row_idx, column=(col_idx + 2))
        ttk.Label(labelframe, text=(language.LEVAL_SPAN + language.COLON)).grid(row=(row_idx + 1), column=col_idx)
        ttk.Entry(labelframe, textvariable=(self.leval_span), width=entry_width).grid(row=(row_idx + 1), column=(col_idx + 1))
        col_idx = 4
        row_idx = 1
        ttk.Label(labelframe, text=(language.GAME_PLAYER_NUM + language.COLON)).grid(row=row_idx, column=col_idx)
        ttk.Entry(labelframe, textvariable=(self.player_num), width=entry_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Checkbutton(labelframe, text=(language.MAIN_WINDOW_EDIT), variable=(self.player_num_editable), command=(self.sw_checkbutton_click)).grid(row=row_idx, column=(col_idx + 2))
        col_idx = 7
        row_idx = 1
        ttk.Checkbutton(labelframe, text=(language.BARCODE_FUNCTION), variable=(self.barcode_function), command=(self.sw_checkbutton_click)).grid(row=row_idx, column=col_idx)
        entry_width = 30
        text_height = 10
        type_name_width = 10
        lf_game_introduce = ttk.LabelFrame(tab2, text=(language.GAME_INTRODUCE))
        lf_game_introduce.pack(fill=BOTH, expand=YES)
        if parent:
            try:
                list_type = list(parent.dict_all_game.keys())
                self.game_type_name.set(list_type[0])
                self.game_type_name2.set(list_type[1])
                self.game_type_name3.set(list_type[2])
                self.game_type_name4.set(list_type[3])
            except:
                pass

        col_idx = 0
        row_idx = 0
        ttk.Label(lf_game_introduce, text=(language.GAME_TYPE_ONE + language.COLON)).grid(row=row_idx, column=col_idx)
        tkinter.Entry(lf_game_introduce, textvariable=(self.game_type_name), width=type_name_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Label(lf_game_introduce, text=(language.GAME_INTRODUCE + language.COLON)).grid(row=row_idx, column=(col_idx + 2))
        text_introduce1 = tkinter.Text(lf_game_introduce, width=entry_width, height=text_height)
        text_introduce1.grid(row=(row_idx + 1), column=(col_idx + 2), rowspan=2)
        text_introduce1.insert(END, self.text_introduce1.get())
        self.text_introduce_widget1 = text_introduce1
        ttk.Label(lf_game_introduce, text=(language.GAME_VIDEO + language.COLON)).grid(row=(row_idx + 1), column=col_idx)
        ttk.Button(lf_game_introduce, text="...", width=5, command=(partial(self.file_select, self.game_type_video))).grid(row=(row_idx + 1), column=(col_idx + 1))
        ttk.Entry(lf_game_introduce, textvariable=(self.game_type_video), width=entry_width).grid(row=(row_idx + 2), column=col_idx, columnspan=2, sticky="nw")
        col_idx = 3
        row_idx = 0
        ttk.Label(lf_game_introduce, text=(language.GAME_TYPE_TWO + language.COLON)).grid(row=row_idx, column=col_idx)
        ttk.Entry(lf_game_introduce, textvariable=(self.game_type_name2), width=type_name_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Label(lf_game_introduce, text=(language.GAME_INTRODUCE + language.COLON)).grid(row=row_idx, column=(col_idx + 2))
        text_introduce2 = tkinter.Text(lf_game_introduce, width=entry_width, height=text_height)
        text_introduce2.grid(row=(row_idx + 1), column=(col_idx + 2), rowspan=2)
        ttk.Label(lf_game_introduce, text=(language.GAME_VIDEO + language.COLON)).grid(row=(row_idx + 1), column=col_idx)
        text_introduce2.insert(END, self.text_introduce2.get())
        self.text_introduce_widget2 = text_introduce2
        ttk.Button(lf_game_introduce, text="...", width=5, command=(partial(self.file_select, self.game_type_video2))).grid(row=(row_idx + 1), column=(col_idx + 1))
        ttk.Entry(lf_game_introduce, textvariable=(self.game_type_video2), width=entry_width).grid(row=(row_idx + 2), column=col_idx, columnspan=2, sticky="nw")
        col_idx = 6
        row_idx = 0
        ttk.Label(lf_game_introduce, text=(language.GAME_TYPE_THREE + language.COLON)).grid(row=row_idx, column=col_idx)
        ttk.Entry(lf_game_introduce, textvariable=(self.game_type_name3), width=type_name_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Label(lf_game_introduce, text=(language.GAME_INTRODUCE + language.COLON)).grid(row=row_idx, column=(col_idx + 2))
        text_introduce3 = tkinter.Text(lf_game_introduce, width=entry_width, height=text_height)
        text_introduce3.grid(row=(row_idx + 1), column=(col_idx + 2), rowspan=2)
        text_introduce3.insert(END, self.text_introduce3.get())
        self.text_introduce_widget3 = text_introduce3
        ttk.Label(lf_game_introduce, text=(language.GAME_VIDEO + language.COLON)).grid(row=(row_idx + 1), column=col_idx)
        ttk.Button(lf_game_introduce, text="...", width=5, command=(partial(self.file_select, self.game_type_video3))).grid(row=(row_idx + 1), column=(col_idx + 1))
        ttk.Entry(lf_game_introduce, textvariable=(self.game_type_video3), width=entry_width).grid(row=(row_idx + 2), column=col_idx, columnspan=2, sticky="nw")
        col_idx = 9
        row_idx = 0
        ttk.Label(lf_game_introduce, text=(language.GAME_TYPE_FOUR + language.COLON)).grid(row=row_idx, column=col_idx)
        ttk.Entry(lf_game_introduce, textvariable=(self.game_type_name4), width=type_name_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Label(lf_game_introduce, text=(language.GAME_INTRODUCE + language.COLON)).grid(row=row_idx, column=(col_idx + 2))
        text_introduce4 = tkinter.Text(lf_game_introduce, width=entry_width, height=text_height)
        text_introduce4.grid(row=(row_idx + 1), column=(col_idx + 2), rowspan=2)
        text_introduce4.insert(END, self.text_introduce4.get())
        self.text_introduce_widget4 = text_introduce4
        ttk.Label(lf_game_introduce, text=(language.GAME_VIDEO + language.COLON)).grid(row=(row_idx + 1), column=col_idx)
        ttk.Button(lf_game_introduce, text="...", width=5, command=(partial(self.file_select, self.game_type_video4))).grid(row=(row_idx + 1), column=(col_idx + 1))
        ttk.Entry(lf_game_introduce, textvariable=(self.game_type_video4), width=entry_width).grid(row=(row_idx + 2), column=col_idx,
          columnspan=2,
          sticky="nw")
        lf_game_video = ttk.LabelFrame(tab2, text=(language.GAME_AUDIO))
        lf_game_video.pack(fill=BOTH, expand=YES)
        col_idx = 0
        row_idx = 1
        ttk.Label(lf_game_video, text=(language.GAME_BG_AUDIO + language.COLON)).grid(row=row_idx, column=(col_idx + 3))
        ttk.Entry(lf_game_video, textvariable=(self.game_bg_audio), width=entry_width).grid(row=row_idx, column=(col_idx + 4))
        ttk.Button(lf_game_video, text="...", width=4, command=(partial(self.file_select, self.game_bg_audio))).grid(row=row_idx, column=(col_idx + 5))
        ttk.Label(lf_game_video, text=(language.GAME_SCODE + language.COLON)).grid(row=row_idx, column=(col_idx + 6))
        ttk.Entry(lf_game_video, textvariable=(self.game_scode), width=entry_width).grid(row=row_idx, column=(col_idx + 7))
        ttk.Button(lf_game_video, text="...", width=4, command=(partial(self.file_select, self.game_scode))).grid(row=row_idx, column=(col_idx + 8))
        ttk.Label(lf_game_video, text=(language.GAME_BLOOD + language.COLON)).grid(row=row_idx, column=(col_idx + 9))
        ttk.Entry(lf_game_video, textvariable=(self.game_blood), width=entry_width).grid(row=row_idx, column=(col_idx + 10))
        ttk.Button(lf_game_video, text="...", width=4, command=(partial(self.file_select, self.game_blood))).grid(row=row_idx, column=(col_idx + 11))
        row_idx = 3
        col_idx = 0
        lf_game_idle = ttk.LabelFrame(tab2, text=(language.GAME_IDLE_VIDEO))
        lf_game_idle.pack(fill=BOTH, expand=YES)
        ttk.Entry(lf_game_idle, textvariable=(self.game_idle_video), width=entry_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Button(lf_game_idle, text="...", width=4, command=(partial(self.file_select, self.game_idle_video))).grid(row=row_idx,
          column=(col_idx + 2))
        row_idx = 0
        col_idx = 0
        lf_video_idle = ttk.LabelFrame(tab2, text=(language.VIDEO_IDLE))
        lf_video_idle.pack(fill=BOTH, expand=YES)
        ttk.Entry(lf_video_idle, textvariable=(self.idle_video), width=entry_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Button(lf_video_idle, text="...", width=4, command=(partial(self.file_select, self.idle_video))).grid(row=row_idx,
          column=(col_idx + 2))
        ttk.Label(lf_video_idle, text=(language.VIDEO_IDLE_TIME)).grid(row=row_idx, column=(col_idx + 3))
        ttk.Entry(lf_video_idle, textvariable=(self.idle_video_time_span), width=5).grid(row=row_idx, column=(col_idx + 4))
        lf_game_other_para = ttk.LabelFrame(tab2, text=(language.GAME_OTHER_PARA))
        lf_game_other_para.pack(fill=BOTH, expand=YES)
        row_idx = 0
        col_idx = 0
        ttk.Label(lf_game_other_para, text=(language.BLUE_HIDE_MAX_TIME + language.COLON)).grid(row=row_idx, column=col_idx)
        ttk.Entry(lf_game_other_para, textvariable=(self.blue_hide_max_time), width=entry_width).grid(row=row_idx, column=(col_idx + 1))
        ttk.Label(lf_game_other_para, text=(language.HIDDEN_SHOW_TIME + language.COLON)).grid(row=row_idx, column=(col_idx + 2))
        ttk.Entry(lf_game_other_para, textvariable=(self.hidden_show_time), width=entry_width).grid(row=row_idx, column=(col_idx + 3))
        ttk.Label(lf_game_other_para, text=(language.PROMPT_SCORE + language.COLON)).grid(row=row_idx, column=(col_idx + 4))
        ttk.Entry(lf_game_other_para, textvariable=(self.hidden_prompt_score), width=entry_width).grid(row=row_idx, column=(col_idx + 5))
        ttk.Label(lf_game_other_para, text=(language.HIDDEN_PROMPT_BREATH_COLOR + language.COLON)).grid(row=row_idx, column=(col_idx + 6))
        ttk.Entry(lf_game_other_para, textvariable=(self.hidden_prompt_breath_color), width=entry_width).grid(row=row_idx, column=(col_idx + 7))
        ttk.Label(lf_game_other_para, text=(language.HIDDEN_TREAD_SHOW_TIME + language.COLON)).grid(row=row_idx, column=(col_idx + 8))
        ttk.Entry(lf_game_other_para, textvariable=(self.hidn_tread_show_time), width=entry_width).grid(row=row_idx, column=(col_idx + 9))
        ttk.Label(lf_game_other_para, text=(language.GAME_RESULT_PROMPT_TM + language.COLON)).grid(row=(row_idx + 1), column=col_idx)
        ttk.Entry(lf_game_other_para, textvariable=(self.game_result_show_time), width=entry_width).grid(row=(row_idx + 1), column=(col_idx + 1))
        lf_game_scode_rule = ttk.LabelFrame(tab2, text=(language.SCODE_RULE))
        lf_game_scode_rule.pack(fill=BOTH, expand=YES)
        row_idx = 0
        col_idx = 0
        ttk.Checkbutton(lf_game_scode_rule, text=(language.SCODE_DIVIDE_PERSON), variable=(self.game_scode_divide_person), command=(self.sw_checkbutton_click)).grid(row=row_idx, column=col_idx)
        row_idx = 0
        col_idx = 1
        ttk.Checkbutton(lf_game_scode_rule, text=(language.SCODE_DIVIDE_TIME), variable=(self.game_scode_divide_time), command=(self.sw_checkbutton_click)).grid(row=row_idx, column=col_idx)
        col_idx = 1
        row_idx = 2
        ttk.Button(tab2, text=(language.UPDATE), command=(lambda: self.sw_setting_conform())).pack()

    def update_led_no_use_table_color(self):
        if self.light.get() or self.screen.get():
            for coors in self.floor_layout_coors_no_use:
                row, col = coors[0] + 1, coors[1] + 1
                self.table_editor.draw_table_cell_color((row, col), Setting.LED_NO_USE_COLOR)

            arr_index = self.wall_posi_del.get().split(",")
            for i in arr_index:
                if i != "":
                    coors = self.wall_light_table[int(i) - 1]
                    self.table_editor.draw_table_cell_color(coors, Setting.LED_NO_USE_COLOR)

        else:
            for coors in self.floor_layout_coors_no_use:
                self.table_editor.draw_table_cell_color(coors, Setting.LED_NO_USE_COLOR)

    def update_led_no_use_arr(self, table_use_state):
        row = len(table_use_state)
        col = len(table_use_state[0])
        self.floor_layout_coors_no_use = []
        if self.light.get() or self.screen.get():
            wall_posi_del = ""
            for i in range(row):
                for j in range(col):
                    if i == 0 or j == 0 or i == row - 1 or j == col - 1:
                        if not table_use_state[i][j]:
                            try:
                                index = self.wall_light_table.index([i, j])
                                wall_posi_del += str(index + 1)
                                wall_posi_del += ","
                            except:
                                pass

                    else:
                        table_use_state[i][j] or self.floor_layout_coors_no_use.append((i - 1, j - 1))

            self.wall_posi_del.set(wall_posi_del)
        else:
            for i in range(row):
                for j in range(col):
                    if not table_use_state[i][j]:
                        self.floor_layout_coors_no_use.append((i, j))

    def call_back_use_led(self, table_use_state):
        set_coors = self.table_editor.get_cur_select_cell_set()
        for coors in set_coors:
            table_use_state[coors[0]][coors[1]] = True

        self.table_editor.update_led_cell_set_color(set_coors, Setting.LED_USE_COLOR)
        self.update_led_no_use_arr(table_use_state)

    def call_back_no_use_led(self, table_use_state):
        set_coors = self.table_editor.get_cur_select_cell_set()
        for coors in set_coors:
            table_use_state[coors[0]][coors[1]] = False

        self.table_editor.update_led_cell_set_color(set_coors, Setting.LED_NO_USE_COLOR)
        self.update_led_no_use_arr(table_use_state)

    def write_wall_light_num_in_table(self, table, table_row, table_col):
        self.calcu_wall_position(table_row - 2, table_col - 2)
        text = 1
        for coors in self.wall_light_table:
            table.write_text_in_table_cell(coors, str(text))
            table.draw_table_cell_color(coors, Color.GREEN)
            text += 1

    def init_led_no_use_table(self, fm_layout_setting_led_table, table_row, table_col):
        rect_table = [[True] * table_col for _ in range(table_row)]
        self.last_size = (table_row, table_col)
        self.last_light = self.light.get()
        if self.light.get() or self.screen.get():
            table_row = table_row + 2
            table_col = table_col + 2
            self.table_led_state = [[True] * table_col for _ in range(table_row)]
            self.table_editor = TableEditor(fm_layout_setting_led_table, self, table_row, table_col)
            self.write_wall_light_num_in_table(self.table_editor, table_row, table_col)
            for coors in self.floor_layout_coors_no_use:
                self.table_led_state[coors[0] + 1][coors[1] + 1] = False
                rect_table[coors[0]][coors[1]] = False

            position_convert.record_led_arr_position_to_rect(self.type, rect_table)
            arr_wall_coors_no_use = self.wall_posi_del.get().split(",")
            for idx in arr_wall_coors_no_use:
                if idx != "":
                    coors = self.wall_light_table[int(idx) - 1]
                    self.table_led_state[coors[0]][coors[1]] = False

            self.draw_table_led_position((self.table_editor), rect_table, wall_light=True)
        else:
            self.table_led_state = [[True] * table_col for _ in range(table_row)]
            self.table_editor = TableEditor(fm_layout_setting_led_table, self, table_row, table_col, head_start=1)
            for coors in self.floor_layout_coors_no_use:
                self.table_led_state[coors[0]][coors[1]] = False
                rect_table[coors[0]][coors[1]] = False

            position_convert.record_led_arr_position_to_rect(self.type, rect_table)
            self.draw_table_led_position(self.table_editor, rect_table)
        self.table_editor.add_right_button_command(label=(language.NO_LED), command=(lambda: self.call_back_no_use_led(self.table_led_state)))
        self.table_editor.add_right_button_command(label=(language.USE_LED), command=(lambda: self.call_back_use_led(self.table_led_state)))
        self.update_led_no_use_table_color()

    def start_edit(self, root, list_com, father_root):
        try:
            self.father_root = father_root
            top = root
            self.list_com = []
            fm_layout_setting = ttk.Frame(top)
            fm_layout_setting.pack(side=TOP, expand=YES)
            style = ttk.Style()
            style.configure("MyFrame.TFrame", background="red")
            fm_layout_setting_left = ttk.Frame(fm_layout_setting)
            fm_layout_setting_left.pack(side=LEFT, expand=YES, anchor="nw")
            self.fm_layout_setting_led_table = ttk.Frame(fm_layout_setting)
            self.fm_layout_setting_led_table.pack(side=LEFT)
            table_row = int(self.value_high.get())
            table_col = int(self.value_width.get())
            self.init_led_no_use_table(self.fm_layout_setting_led_table, table_row, table_col)
            cur_row = 0
            fm_top_pro = ttk.LabelFrame(fm_layout_setting_left, text=(language.LED_LAYOUT))
            fm_top_pro.pack(side=TOP, pady=10, anchor="w")
            ttk.Label(fm_top_pro, text=(language.COL + ":")).grid(row=2, column=0, rowspan=1, columnspan=1)
            en_width = ttk.Entry(fm_top_pro, textvariable=(self.value_width), width=4)
            en_width.grid(row=2, column=1, columnspan=2)
            ttk.Label(fm_top_pro, text=(language.ROW + ":")).grid(row=2, column=3)
            en_high = ttk.Entry(fm_top_pro, textvariable=(self.value_high), width=4)
            en_high.grid(row=2, column=4, columnspan=2)
            ttk.Label(fm_top_pro, text=(language.START_FROM)).grid(row=3, column=0, rowspan=1, columnspan=1)
            value_from_list = [language.LEFT_UP, language.RIGHT_UP, language.LEFT_DOWN, language.RIGHT_DOWN]
            combo_from = ttk.Combobox(fm_top_pro, state="readonly", textvariable=(self.value_from), values=value_from_list, width=8)
            combo_from.grid(row=3, column=1, rowspan=1, columnspan=2)
            cur_row = 3
            cur_row += 1
            ttk.Label(fm_top_pro, text=(language.DIRECTION)).grid(row=3, column=3)
            self.list_direction = self.get_director(self.value_from.get())
            combo_direction = ttk.Combobox(fm_top_pro, state="readonly", textvariable=(self.value_direction), values=(self.list_direction),
              width=4)
            combo_from.bind("<<ComboboxSelected>>", lambda event: self.choose(event, combo_from, combo_direction))
            combo_direction.grid(row=3, column=4, rowspan=1, columnspan=2)
            ttk.Label(fm_top_pro, text=(language.CORNER_LINE_START)).grid(row=4, column=0)
            ttk.Entry(fm_top_pro, textvariable=(self.corner_line_start), width=4).grid(row=4, column=1)
            fm_wall_setting = ttk.LabelFrame(fm_layout_setting_left, text=(language.WALL_LAYOUT))
            fm_wall_setting.pack(side=TOP, anchor="nw", pady=10)
            fm_wall_checkbox = ttk.Frame(fm_wall_setting)
            fm_wall_checkbox.pack(side=LEFT)
            row_idx = 0
            ttk.Checkbutton(fm_wall_checkbox, text=(language.LIGHT), variable=(self.light), command=(lambda: self.check_click(0))).grid(row=row_idx, column=1, pady=10)
            ttk.Checkbutton(fm_wall_checkbox, text=(language.SCREEN), variable=(self.screen), command=(lambda: self.check_click(1))).grid(row=row_idx, column=2)
            fm_wall = ttk.Frame(fm_wall_setting)
            fm_wall.pack(side=LEFT)
            ttk.Label(fm_wall, text=(language.WALL_LAYOUT_START)).grid(row=2, column=0)
            ttk.Entry(fm_wall, textvariable=(self.wall_start), width=5).grid(row=2, column=1)
            ttk.Label(fm_wall, text=(language.WALL_LAYOUT_DIRECTION)).grid(row=2, column=3)
            ttk.Combobox(fm_wall, textvariable=(self.wall_direct), values=["right", "left"], width=5).grid(row=2, column=4)
            fm_server = ttk.Frame(top)
            fm_server.pack(side=TOP, fill=BOTH, expand=YES)
            ttk.Label(fm_server, text=(language.SEVER_IP)).grid(row=0, column=0)
            ttk.Entry(fm_server, textvariable=(self.ip_address)).grid(row=0, column=1)
            fm_local_ip = fm_server
            ttk.Label(fm_local_ip, text=(language.LOCAL_IP)).grid(row=1, column=0)
            ttk.Entry(fm_local_ip, textvariable=(self.local_ip_address)).grid(row=1, column=1)
            ttk.Label(fm_local_ip, text=(language.LOCAL_PORT)).grid(row=2, column=0)
            ttk.Entry(fm_local_ip, textvariable=(self.local_ip_port)).grid(row=2, column=1)
            fm_table_introduce = ttk.LabelFrame(fm_layout_setting_left, text=(language.TABLE_INTRODUCE))
            fm_table_introduce.pack(side=TOP, anchor="nw", pady=2)
            Label(fm_table_introduce, text="", background="green", width=2).pack(side=LEFT)
            Label(fm_table_introduce, text=(language.TABLE_CELL_GREEN)).pack(side=LEFT)
            Label(fm_table_introduce, text="", background=(Setting.LED_NO_USE_COLOR_FORMAT), width=2).pack(side=LEFT)
            Label(fm_table_introduce, text=(language.TABLE_CELL_YELLOW)).pack(side=LEFT)
            fm_hardware = ttk.LabelFrame(fm_layout_setting_left, text=(language.HARDWARE_CONNECTION))
            self.fm_hardware = fm_hardware
            fm_hardware.pack(side=TOP, pady=10, fill=BOTH, expand=YES)
            fm_hardware_title = ttk.Frame(fm_hardware)
            fm_hardware_title.pack(side=TOP, fill=BOTH, expand=YES)
            self.fm_hardware_content = ttk.Frame(fm_hardware)
            self.fm_hardware_content.pack()
            ttk.Button(fm_hardware_title, text=(language.SCAN), command=(lambda: self.btn_hardware_scan_new(self.fm_hardware_content))).pack(side=LEFT, padx=10)
            self.fm_hardware_content = ttk.Frame(fm_hardware)
            self.fm_hardware_content.pack()
            list_com_name = self.list_com_name
            self.last_list_com_scan = []
            self.list_controler_var = []
            i = 1
            self.dyna_display_com_widget(self.list_com_info)
            self.dyna_display_com_widget(self.list_wall_com_info)
            self.dyna_display_com_widget(self.list_screen_com_info)
            btn_comform = ttk.Button(top, text=(language.UPDATE), command=(lambda: self.btn_comform(fm_layout_setting)))
            btn_comform.pack()
            self.dict_com_info = dict()
        except:
            logger.error(traceback.format_exc())

    def quit(self):
        if self.master:
            self.master.destroy()

    def close_com_thread(self):
        text_var_index = 5
        for com_info_arr in self.list_controler_var:
            if com_info_arr[text_var_index].get() != language.TEST:
                self.dict_com_obj_thread[self.get_com_num(com_info_arr[0].get())].stop()
            com_info_arr[text_var_index].set(language.TEST)

    def customized_function(self):
        self.close_com_thread()
        self.master.destroy()

# okay decompiling /Users/apple/Desktop/activerse/climb/climb_source_code/gui/gui_setting.pyc
