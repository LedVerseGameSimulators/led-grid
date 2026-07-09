# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: gui2\ui_player_setting.py
import datetime, shelve
from tkinter import Toplevel, Frame, ttk, StringVar, YES, BOTH, Entry, IntVar, messagebox
from database.db_operation import DBOperation
from gui.gui_editor_game import EditorGame
import gui.language as language
from model.setting import Setting

class UIPlayerSetting:

    def read_game_info(self, game_name):
        db = shelve.open(Setting.GAME_RESULT_DIRECTOR + game_name)
        game = db[game_name]
        db.close()
        return game

    def add_new_player(self, fm_1, num):
        if self.list_participate is not None:
            if len(self.list_participate) > 0:
                time_consume = self.list_participate[num - 1].get() * self.game_time.get()
                custom_id = self.list_phone_num[num - 1].get()
                result = self.db.search_custom_by_phone(str(int(custom_id)))
                custom_time_left = float(result[0][-1]) - time_consume
                if custom_time_left < 0:
                    messagebox.showerror((language.GAME_PROMPT), (language.GAME_INSUFFICIENT + str(result[0][-1])), parent=(self.root))
                    return
        col_idx = 0
        row_idx = num + 1
        ttk.Label(fm_1, text=(language.PLAYER + str(row_idx))).grid(row=row_idx, column=col_idx)
        phone_num = StringVar()
        self.list_phone_num.append(phone_num)
        en_number = ttk.Entry(fm_1, textvariable=phone_num)
        en_number.bind("<Return>", lambda event: self.add_new_player(fm_1, row_idx))
        en_number.focus_set()
        en_number.grid(row=row_idx, column=(col_idx + 1))
        participate_num = IntVar()
        participate_num.set(1)
        self.list_participate.append(participate_num)
        ttk.Label(fm_1, text=(language.PARTICIPATE)).grid(row=row_idx, column=(col_idx + 2))
        en_participate = ttk.Entry(fm_1, textvariable=participate_num, width=12)
        en_participate.grid(row=row_idx, column=(col_idx + 3))

    def comform(self):
        i = 0
        custom_time_left = 0
        time_consume = 0
        tmp_list_custom_id = []
        for custom_id in self.list_phone_num:
            custom_id = custom_id.get()
            if custom_id != "":
                time_consume = self.list_participate[i].get() * self.game_time.get()
                result = self.db.search_custom_by_phone(str(int(custom_id)))
                str_var = StringVar()
                str_var.set(result[0][0])
                tmp_list_custom_id.append(str_var)
                custom_time_left = float(result[0][-1]) - time_consume
                if custom_time_left < 0:
                    messagebox.showerror((language.GAME_PROMPT), (language.GAME_CUSTOM + str_var.get() + language.GAME_INSUFFICIENT),
                      parent=(self.root))
                    return

        self.list_phone_num = tmp_list_custom_id
        str_num = ""
        play_nums = 0
        for num in self.list_phone_num:
            num = num.get()
            if num != "":
                str_num += num
                str_num += ","
                play_nums += 1

        str_num = str_num[0[:-1]]
        rowcount = self.db.insert_player_group(str(play_nums), str_num)
        last_id_player = self.db.select_last_insert_id()
        self.player_group_id = last_id_player
        str_num = ""
        for num in self.list_game_name:
            num = num
            str_num += num
            str_num += ","

        str_num = str_num[0[:-1]]
        rowcount = self.db.insert_game_group(str(len(self.list_game_name)), str(play_nums), str(self.setting.game_leval.get()), str_num)
        last_id_game = self.db.select_last_insert_id()
        self.game_group_id = last_id_game
        time_now = datetime.datetime.now()
        str_time = time_now.__format__("%Y-%m-%d %H:%M:%S")
        rowcount = self.db.insert_game_comsume(str_time, str(self.game_time.get()), last_id_game, last_id_player)
        game_consume_id = self.db.select_last_insert_id()
        i = 0
        for custom_id in self.list_phone_num:
            custom_id = custom_id.get()
            self.db.update_custom_info_by_id((str(int(custom_id))), time_left=custom_time_left)
            self.db.insert_custom_comsume(str(int(custom_id)), str(game_consume_id), str(self.list_participate[i].get()), str(self.game_time.get()), str(time_consume))

        self.customized_function()
        EditorGame(self, self.parent.image_file, self.list_game_name, self.parent.bg_image_file, self.game_time.get())

    def __init__(self, parent, list_game_name):
        root = Toplevel()
        self.root = root
        self.parent = parent
        self.setting = parent.setting
        self.list_game_name = list_game_name
        self.db = parent.db
        fm_2 = Frame(root)
        fm_2.pack(expand=YES, fill=BOTH)
        row_idx = 0
        col_idx = 0
        ttk.Label(fm_2, text=(language.GAME_TIME)).grid(row=row_idx, column=col_idx)
        self.game_time = IntVar()
        en_game_time = ttk.Entry(fm_2, textvariable=(self.game_time), width="5")
        en_game_time.grid(row=row_idx, column=(col_idx + 1))
        ttk.Label(fm_2, text=(language.GAME_MIN)).grid(row=row_idx, column=(col_idx + 2))
        fm_1 = Frame(root)
        fm_1.pack(expand=YES, fill=BOTH)
        ttk.Label(fm_1, text=(language.PLAYER_NUMBER + language.GAME_PLAYER_ADD_INTRO)).grid(row=row_idx, column=col_idx)
        self.list_phone_num = []
        self.list_participate = []
        self.add_new_player(fm_1, 0)
        ttk.Button(root, text=(language.CONFIRM), command=(lambda: self.comform())).pack(fill=BOTH, expand=YES)
        root.update()
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        scnWidth, scnHeight = root.maxsize()
        tmpcnf = "+%d+%d" % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol("WM_DELETE_WINDOW", self.customized_function)
        root.iconbitmap("./photo/ledplay.ico")
        root.title(language.PLAYER_SETTING)
        root.grab_set()
        root.mainloop()

    def customized_function(self):
        self.root.destroy()
        return

# okay decompiling /games/climb/climb_source_code/gui2/ui_player_setting.pyc
