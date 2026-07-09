# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.14.4 (main, Apr  7 2026, 13:13:20) [Clang 17_iter__iter_ (clang-1700.6.4.2)]
# Embedded file name: app_gui.py
import locale, shelve, sys, time, traceback
from tkinter import *
from tkinter import ttk, filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
from loguru import logger
import gui.gui_setting as gui_setting
import gui.gui_debugging as gui_debugging
from datetime import datetime
from database.db_operation import DBOperation
from encryption import yanqian
from audio_play import audio
import gui.language as language
from gui2.ui_player_setting import UIPlayerSetting
from model.setting import Setting

class AppUI:

    def btn_comform(self):
        if yanqian.yanqian():
            list_index = self.lb_game_type.curselection()
            list_item = []
            for index in list_index:
                list_item.append(self.lb_game_type.get(index))

            UIPlayerSetting(self, list_item)
        else:
            ret = messagebox.showwarning(language.AUTHOR, language.UN_AUTHOR)

    def btn_add_game(self):
        file_path = filedialog.askopenfilename(parent=(self.root), initialdir=(Setting.GAME_RESULT_DIRECTOR))
        if file_path is not None:
            if file_path != "":
                arr_file_path = file_path.split(".")
                file_name = arr_file_path[0].split("/")[-1]
                self.game_name_list.append(file_name)
                self.lb_game_type.select_set(0)
                self.list_var.set(self.game_name_list)

    def btn_dele_game(self):
        list_index = self.lb_game_type.curselection()
        for i in range(len(list_index) - 1, -1, -1):
            self.game_name_list.pop(list_index[i])

        self.list_var.set(self.game_name_list)

    def init_widgets(self, list_game_name):
        fm1 = ttk.Frame(self.root)
        scnWidth, scnHeight = self.root.maxsize()
        fm1.pack(side=TOP, fill=BOTH, expand=True)
        ttk.Label(fm1, text=(language.LAMP), font=('STKaiti', 20)).pack()
        fm2 = ttk.Frame(self.root)
        fm2.pack(fill=BOTH, expand=YES)
        fm_game_type = ttk.Frame(fm2)
        fm_game_type.pack(side=LEFT, fill=BOTH, expand=YES)
        ttk.Label(fm_game_type, text=(language.GAME)).pack(side=TOP, fill=BOTH, expand=YES)
        sb_game_type = ttk.Scrollbar(fm_game_type)
        self.list_var = StringVar(value=(self.game_name_list))
        self.lb_game_type = Listbox(fm_game_type, selectmode=MULTIPLE, yscrollcommand=(sb_game_type.set),
          font=("STKaiti", int(0.020833333333333332 * scnWidth)),
          listvariable=(self.list_var))
        self.lb_game_type.select_set(0)
        self.lb_game_type.pack(side=LEFT, expand=YES, ipadx=10)
        sb_game_type.config(command=(self.lb_game_type.yview()))
        fm_ranking = ttk.Frame(fm2)
        ttk.Label(fm_ranking, text=(language.RANKING_LIST)).pack(side=TOP, fill=BOTH, expand=YES)
        sb_ranking = ttk.Scrollbar(fm_ranking)
        lb_ranking = Listbox(fm_ranking, yscrollcommand=(sb_ranking.set), font=("STKaiti", int(0.020833333333333332 * scnWidth)))
        lb_ranking.insert(END, "team1,score=100")
        lb_ranking.insert(END, "team2,score=90")
        lb_ranking.pack(side=LEFT, fill=BOTH, expand=YES)
        sb_ranking.config(command=(lb_ranking.yview()))
        style = ttk.Style()
        style.configure("TButton", font=("STKaiti", int(0.020833333333333332 * scnWidth)))
        fm_game_oper = Frame(self.root)
        fm_game_oper.pack(fill=BOTH, expand=YES)
        btn_add_game = ttk.Button(fm_game_oper, text=(language.ADD_GAME), command=(self.btn_add_game))
        btn_add_game.pack(side=LEFT, fill=BOTH, expand=YES)
        btn_dele_game = ttk.Button(fm_game_oper, text=(language.DELE_GAME), command=(self.btn_dele_game))
        btn_dele_game.pack(side=LEFT, fill=BOTH, expand=YES)
        btn_comform = ttk.Button(fm_game_oper, text=(language.PLAY_NOW), command=(self.btn_comform), style="TButton")
        btn_comform.pack(side=LEFT, fill=BOTH, expand=YES)

    def read_list_game_name(self):
        try:
            f = shelve.open("./setting/led_parameter")
            list_name = f[Setting.LIST_GAME_NAME]
            f.close()
        except:
            list_name = []

        return list_name

    def save_list_game_name(self):
        f = shelve.open("./setting/led_parameter")
        f[Setting.LIST_GAME_NAME] = self.game_name_list
        f.close()

    def select_game_director(self, root):
        directory_path = filedialog.askdirectory(parent=root)
        self.game_director.set(directory_path)

    def __init__(self, parent, setting, debug, language_setting):
        root = Toplevel(master=(parent.root))
        self.root = root
        scnWidth, scnHeight = root.maxsize()
        self.scnWidth = scnWidth
        self.scnHeight = scnHeight
        self.parent = parent
        language(language_setting.get())
        self.create_menu(root, language_setting)
        self.debug = debug
        self.setting = setting
        notebook = ttk.Notebook(root)
        notebook.pack(fill=BOTH, expand=YES)
        tab1 = Frame(notebook)
        tab1.pack(fill=BOTH, expand=YES)
        tab2 = Frame(notebook)
        tab2.pack(fill=BOTH, expand=YES)
        notebook.add(tab1, text=(language.HARDWARE_SETTING))
        notebook.add(tab2, text=(language.SOFTWARE_SETTING))
        setting.start_edit(tab1, [], root)
        setting.software_setting(root, tab2, parent)
        root.update()
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        scnWidth, scnHeight = root.maxsize()
        tmpcnf = "+%d+%d" % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol("WM_DELETE_WINDOW", self.customized_function)
        root.iconbitmap("./photo/ledplay.ico")
        root.title(language.SETTING)
        root.grab_set()

    def create_menu(self, root, language_setting):
        menu = Menu(root, font=("STKaiti", int(0.020833333333333332 * self.scnWidth)))
        menu.add_command(label=(language.DEBUG), command=(self.debug), font=("STKaiti", int(0.010416666666666666 * self.scnWidth)))
        menu.add_command(label=(language.ABOUT), command=(self.about), font=("STKaiti", int(0.010416666666666666 * self.scnWidth)))
        menu.configure(font=("Verdana", int(0.010416666666666666 * self.scnWidth)))
        menu_sub = Menu(menu)
        menu_sub.add_radiobutton(label=(language.LANG_CHINESE), variable=language_setting, value=0, command=(lambda: self.language(language_setting)))
        menu_sub.add_radiobutton(label=(language.LANG_ENGLISH), variable=language_setting, value=1, command=(lambda: self.language(language_setting)))
        menu_sub.add_radiobutton(label=(language.LANG_SPAIN), variable=language_setting, value=2, command=(lambda: self.language(language_setting)))
        menu_sub.add_radiobutton(label=(language.LANG_FRENCH), variable=language_setting, value=3, command=(lambda: self.language(language_setting)))
        menu.add_cascade(label=(language.LANG), menu=menu_sub)
        root["menu"] = menu

    def setting(self):
        self.setting.start_edit([], self.root)

    def debug(self):
        self.debug.start_edit()

    def customized_function(self):
        logger.info("setting ui close")
        try:
            self.setting.close_com_thread()
            self.parent.refresh_ui_data()
            self.parent.open_idle_activity()
            self.root.destroy()
            self.parent.gui_setting_opened = False
        except:
            logger.error("setting ui close {}", traceback.format_exc())

    def language(self, language_setting):
        ret = messagebox.askokcancel("程序关闭重新打开后生效", "确定关闭重新打开？")
        if not ret:
            f = shelve.open("./setting/language_parameter")
            language_setting.set(f.get("language_var"))
            f.close()
        else:
            f_language = shelve.open("./setting/language_parameter")
            cur_language = language_setting.get()
            last_language = f_language.get("language_var")
            f_language["language_var"] = cur_language
            f_language.close()
            self.root.destroy()

    def about(self):
        verson = "Led play ver: 1.2.1"
        self.verson = verson
        ret = messagebox.showinfo("版本", (self.verson + "\n" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")), master=(self.root))

# okay decompiling /Users/apple/Desktop/activerse/climb/climb_source_code/gui/app_gui.pyc
