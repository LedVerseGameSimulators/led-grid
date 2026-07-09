# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.14.4 (main, Apr  7 2026, 13:13:20) [Clang 17_iter__iter_ (clang-1700.6.4.2)]
# Embedded file name: gui_countdown.py
import time, tkinter
from tkinter import Toplevel, ttk, YES, BOTH
from tkinter.ttk import Frame
from loguru import logger
from model.setting import Setting
from util.gm_introduce_video_new import TkVideoPlayNew

class GuiCountDown:

    def __init__(self, main_obj, parent, player_num_cur=0, tourist_name="", list_player_cur=[], game_type_idx=0, game_idx=0, game_time=None, flag=0):
        self.countdown_video = None
        main_obj.game_record_rt.running_to_obj = self
        main_obj.game_record_rt.running_to_flag = 3
        self.player_num = player_num_cur
        self.tourist_name = tourist_name
        self.list_player = list_player_cur
        self.parent = parent
        self.main_obj = main_obj
        self.flag = flag
        self.game_type_idx = game_type_idx
        self.game_idx = game_idx
        self.game_time = game_time
        root = Toplevel(master=(self.main_obj.root))
        root.attributes("-topmost", "true")
        print("game ui root create")
        self.root = root
        self.full_screen = True
        root.attributes("-fullscreen", Setting.FULL_SCREEN)
        scnWidth, scnHeight = root.maxsize()
        fm_main = Frame(root)
        fm_main.pack(expand=YES, fill=BOTH)
        lb_img = tkinter.Label(fm_main, borderwidth=0, border=0, width=scnWidth, height=scnHeight)
        lb_img.pack(expand=YES, fill=BOTH)
        video_path = ".\\audio\\countdown.mp4"
        self.countdown_video = TkVideoPlayNew(video_path, lb_img, loop=1, video_size=(scnWidth, scnHeight))
        self.countdown_video.start()
        self.is_not_interrupt = True
        curWidth = scnWidth
        curHeight = scnHeight
        print(curWidth, curHeight)
        scnWidth, scnHeight = root.maxsize()
        tmpcnf = "+%d+%d" % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.iconbitmap("./photo/ledplay.ico")
        while not self.countdown_video.running_ending:
            time.sleep(0.01)
            root.update()

        if parent:
            parent.customized_function()
        elif self.is_not_interrupt:
            self.next()
        else:
            main_obj.game_record_rt.running_to_flag = 0
            root.destroy()

    def running(self, root, lb_img, countdown_video):
        if countdown_video.running_ending:
            countdown_video.join()
            root.quit()
            if self.is_not_interrupt:
                self.next()
        else:
            root.after(100, self.running, root, lb_img, countdown_video)

    def customized_function(self):
        self.is_not_interrupt = False
        self.countdown_video.close_video(self.root)

    def next(self):
        if self.flag:
            self.main_obj.game_start_remote(player_num_cur=(self.player_num), game_type_idx=(self.game_type_idx), game_idx=(self.game_idx),
              game_time=(self.game_time),
              tourist_name=(self.tourist_name),
              root=(self.root))
        else:
            self.main_obj.game_start(player_num_cur=(self.player_num), tourist_name=(self.tourist_name), list_player_cur=(self.list_player),
              root=(self.root))

    def close(self):
        self.root.destroy()

# okay decompiling /Users/apple/Desktop/activerse/climb/climb_source_code/gui/gui_countdown.pyc
