# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.14.4 (main, Apr  7 2026, 13:13:20) [Clang 17_iter__iter_ (clang-1700.6.4.2)]
# Embedded file name: gui_debugging.py
from tkinter import *
from tkinter import ttk
import shelve
import gui.language as language

class Debugging:

    def __init__(self):
        self.read_parameter()

    def read_parameter(self):
        f = shelve.open("./setting/debug_parameter")
        list_com = []
        try:
            self.tread_red_time = StringVar()
            tread_red_time = f.get("tread_red_time")
            if tread_red_time is None:
                self.tread_red_time.set("0.2")
            else:
                self.tread_red_time.set(tread_red_time)
            self.life_value_count_time = StringVar()
            life_value_count_time = f.get("life_value_count_time")
            if life_value_count_time is None:
                self.life_value_count_time.set("1.2")
            else:
                self.life_value_count_time.set(life_value_count_time)
            self.com_is_block = BooleanVar()
            com_is_block = f.get("com_is_block")
            if com_is_block is None:
                self.com_is_block.set(False)
            else:
                self.com_is_block.set(com_is_block)
            self.log = BooleanVar()
            log = f.get("log")
            if log is None:
                self.log.set(True)
            else:
                self.log.set(log)
            self.game_display = BooleanVar()
            game_display = f.get("game_display")
            if game_display is None:
                self.game_display.set(True)
            else:
                self.game_display.set(game_display)
            self.hardware_connection = BooleanVar()
            hardware_connection = f.get("hardware_connection")
            if hardware_connection is None:
                self.hardware_connection.set(True)
                f["hardware_connection"] = True
            else:
                self.hardware_connection.set(hardware_connection)
        except:
            self.tread_red_time = StringVar()
            self.tread_red_time.set("0.1")
            self.life_value_count_time = StringVar()
            self.life_value_count_time.set("1.2")
            self.com_is_block = BooleanVar()
            self.com_is_block.set(False)
            self.log = BooleanVar()
            self.log.set(True)
            self.game_display = BooleanVar()
            self.game_display.set(True)
            self.hardware_connection.set(True)

        f.close()

    def save_parameter(self):
        f = shelve.open("./setting/debug_parameter")
        f["tread_red_time"] = self.tread_red_time.get()
        f["life_value_count_time"] = self.life_value_count_time.get()
        f["com_is_block"] = self.com_is_block.get()
        f["log"] = self.log.get()
        f["game_display"] = self.game_display.get()
        f["hardware_connection"] = self.hardware_connection.get()
        f.close()

    def btn_comform(self):
        self.save_parameter()

    def start_edit(self):
        top = Toplevel()
        scnWidth, scnHeight = top.maxsize()
        self.master = top
        top.title(language.DEBUG)
        fm_top_pro = ttk.Frame(top)
        fm_top_pro.pack(side=TOP, pady=10)
        ttk.Label(fm_top_pro, text="", font=("STKaiti", int(0.0078125 * scnWidth))).grid(row=1, column=0, columnspan=1, pady=20)
        ttk.Label(fm_top_pro, text=(language.TREAD_DURATION), font=("STKaiti", int(0.0078125 * scnWidth))).grid(row=2, column=0, columnspan=1)
        en_tread = ttk.Entry(fm_top_pro, textvariable=(self.tread_red_time), font=("STKaiti", int(0.0078125 * scnWidth)))
        en_tread.grid(row=3, column=0, columnspan=2)
        ttk.Label(fm_top_pro, text=(language.SHED_BLOOD_DURATION), font=("STKaiti", int(0.0078125 * scnWidth))).grid(row=4, column=0)
        en_life_value = ttk.Entry(fm_top_pro, textvariable=(self.life_value_count_time), font=("STKaiti", int(0.0078125 * scnWidth)))
        en_life_value.grid(row=5, column=0, columnspan=2)
        style = ttk.Style(fm_top_pro)
        style.configure("TCheckbutton", font=("STKaiti", int(0.0078125 * scnWidth)))
        style.configure("TButton", font=("STKaiti", int(0.0078125 * scnWidth)))
        cb_block = ttk.Checkbutton(fm_top_pro, text=(language.SERIAL_PORT_BLOCKING), variable=(self.com_is_block))
        cb_block.grid(row=6, column=0, columnspan=2)
        cb_log = ttk.Checkbutton(fm_top_pro, text=(language.LOG), variable=(self.log))
        cb_log.grid(row=7, column=0, columnspan=2)
        cb_display_game = ttk.Checkbutton(fm_top_pro, text=(language.GAME_DISPLAY), variable=(self.game_display))
        cb_display_game.grid(row=8, column=0, columnspan=2)
        cb_display_game = ttk.Checkbutton(fm_top_pro, text=(language.GAME_DISPLAY), variable=(self.game_display))
        cb_display_game.grid(row=8, column=0, columnspan=2)
        cb_hardware_connection_game = ttk.Checkbutton(fm_top_pro, text=(language.HARDWARE_CONNECTION), variable=(self.hardware_connection))
        cb_hardware_connection_game.grid(row=9, column=0, columnspan=2)
        btn_comform = ttk.Button(top, text=(language.CONFIRM), command=(self.btn_comform))
        btn_comform.pack()
        self.dict_com_info = dict()
        top.resizable(False, False)
        top.update()
        curWidth = top.winfo_width()
        curHeight = top.winfo_height()
        scnWidth, scnHeight = top.maxsize()
        tmpcnf = "+%d+%d" % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        top.geometry(tmpcnf)
        top.protocol("WM_DELETE_WINDOW", self.customized_function)
        top.iconbitmap("./photo/ledplay.ico")
        top.grab_set()

    def quit(self):
        if self.master:
            self.master.destroy()

    def customized_function(self):
        self.master.destroy()

# okay decompiling /Users/apple/Desktop/activerse/climb/climb_source_code/gui/gui_debugging.pyc
