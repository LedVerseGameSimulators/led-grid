# Source Generated with Decompyle++
# File: gui_game_main.pyc (Python 3.7)

import datetime
import locale
import os
import shelve
import sys
import threading
import time
import tkinter
import traceback
from multiprocessing import Process, Pipe
from tkinter import ttk, BOTH, YES, Canvas, Image, Tk, VERTICAL, Y, RIGHT, LEFT, messagebox
from functools import partial
import loguru
from PIL import ImageTk, Image, ImageGrab
from loguru import logger
import gui.app_gui as gui
from audio_play import audio
from database.db_operation import DBOperation
from encryption import yanqian
from game_play.game_running import GameRunning
from gui import gui_debugging, gui_setting
from gui.gui_countdown import GuiCountDown
from gui.gui_game import GuiGame
from gui.gui_game_level_select import GameLevelSelect
from gui.gui_game_ranking_canvas import GameRankingCanvas
from gui.language import language
from model.setting import Setting
from model_in.game_record_rt import GameRecordRT
from net.net_socket import NetSocket
from tourist_record.tourist_record_main import TouristRecord
from ui_design.button_canvas import Button_Canvas
from util.gm_introduce_video_new import TkVideoPlayNew
from util.idle_video_play import IdleVideoPlay
from util.image_process import ImageProcess
from util.input_listener import InputListener
from net import net_socket
from multiprocessing.connection import Connection

def process_run():
    game_idle = None
    my_log = logger.add('./log/led_play_runtime.log', '1 days', '100 MB', 'INFO', **('retention', 'rotation', 'level'))
    game_idle = GameRunning()
    game_idle.star_running()


class GuiMain:
    
    def message_controller(self = None, conn = None):
        self.program_running = True
        while self.program_running:
            rcvdata = conn.recv()
            print(rcvdata)

    
    def dict_all_game_copy(self, dict_all_game):
        dict_game_name_new = dict()
        for key, value_list in dict_all_game.items():
            value_list_new = []
            for value in value_list:
                value_list_new.append(value.split('.')[0])
            
            dict_game_name_new[key] = value_list_new
        
        return dict_game_name_new

    
    def finish_game(self):
        self.reset_after_game_time_out()

    
    def game_start(self, player_num_cur, tourist_name, list_player_cur, root = (0, '', [], None)):
        ret = True
        self.game_record_rt.game_state = Setting.GAME_NORMAL
        dict_all_game = self.dict_all_game_copy(self.dict_all_game)
        last_game_type = self.last_game_type
        last_game_name = self.last_game_name
        game_record_rt = self.game_record_rt
        game_time = self.game_time
        barcode_function = self.setting.barcode_function.get()
        player_num = self.player_num
        if player_num_cur != 0:
            player_num = player_num_cur
        self.player_num = player_num
        entry_user_name = self.entry_user_name
        if tourist_name != '':
            entry_user_name = tourist_name
        self.entry_user_name = entry_user_name
        list_player = self.list_player
        if list_player_cur != []:
            list_player = list_player_cur
        self.list_player = list_player
        main_obj = self
        life_value = self.life_value
        game_record_rt.game_blood = self.life_value
        game_record_rt.game_blood_right = self.life_value
        game_record_rt.game_blood_left = self.life_value
        if yanqian.yanqian():
            game_type = 'file'
            list_game_type = list(dict_all_game.keys())
            game_type_length = len(list_game_type)
            type_index = list_game_type.index(last_game_type.value)
            if type_index == 3:
                game_type = 'module'
            else:
                game_type_length -= 1
            list_game = dict_all_game[last_game_type.value]
            game_index = list_game.index(last_game_name.value)
            list_game_path = []
            list_game = self.dict_all_game[last_game_type.value]
            for j in range(game_index, len(list_game)):
                list_game_path.append('.//source//' + last_game_type.value + '//' + list_game[j])
            
            for i in range(type_index + 1, game_type_length):
                list_game = self.dict_all_game[list_game_type[i]]
                for j in range(len(list_game)):
                    list_game_path.append('.//source//' + list_game_type[i] + '//' + list_game[j])
                
            
            game_time_pass = game_record_rt.get_game_time_pass()
            game_time = game_time - game_time_pass
            game_record_rt.game_time_left = game_time * 60
            if game_type == 'file':
                
                try:
                    if barcode_function and player_num > 0 and len(list_player) >= player_num:
                        self.gui_game = GuiGame(main_obj, life_value, list_game_path, barcode_function, game_time, list_player, root, **('last_root',))
                    elif barcode_function and player_num > 0:
                        list_player = []
                        for i in range(player_num):
                            list_player.append('')
                        
                        if entry_user_name == '':
                            list_player[0] = language.TOURIST + str(datetime.datetime.now().month) + str(datetime.datetime.now().day) + str(datetime.datetime.now().hour) + str(datetime.datetime.now().minute)
                        else:
                            list_player[0] = entry_user_name
                        self.gui_game = GuiGame(main_obj, life_value, list_game_path, barcode_function, game_time, list_player, root, **('last_root',))
                    else:
                        ret = messagebox.showerror(language.GAME_PLAYER, language.NO_SET, root, **('parent',))
                        ret = False
                except:
                    logger.error('{}', traceback.format_exc())
                    ret = False

            else:
                
                try:
                    if barcode_function and player_num > 0 and len(list_player) >= player_num:
                        self.gui_game = GuiGame(main_obj, life_value, list_game_path, barcode_function, game_time, list_player, root, **('last_root',))
                    elif barcode_function and player_num > 0:
                        list_player = []
                        for i in range(player_num):
                            list_player.append('')
                        
                        if entry_user_name == '':
                            list_player[0] = language.TOURIST + str(datetime.datetime.now().month) + str(datetime.datetime.now().day) + str(datetime.datetime.now().hour) + str(datetime.datetime.now().minute)
                        else:
                            list_player[0] = entry_user_name
                        self.gui_game = GuiGame(main_obj, life_value, list_game_path, barcode_function, game_time, list_player, root, **('last_root',))
                    else:
                        messagebox.showerror(language.GAME_PLAYER, language.NO_SET, root, **('parent',))
                        ret = False
                except:
                    logger.error('{}', traceback.format_exc())
                    ret = False

            logger.info('end of main start game')
            self.finish_game()
        else:
            ret = messagebox.showwarning(language.AUTHOR, language.UN_AUTHOR, root, **('parent',))
            ret = False
        return ret

    
    def is_game_num_exist(self, game_type_idx, game_index):
        dict_all_game = self.dict_all_game
        list_game_type = list(dict_all_game.keys())
        game_type_length = len(list_game_type)
        if game_type_idx > game_type_length - 1 or game_type_idx < 0:
            self.game_record_rt.game_state = Setting.GAME_NUMBER_ERROR
            return False
        list_game = None(self.dict_all_game.values())[game_type_idx]
        if game_index < 0 or game_index > len(list_game):
            self.game_record_rt.game_state = Setting.GAME_NUMBER_ERROR
            return False

    
    def game_start_remote(self, player_num_cur, tourist_name, list_player_cur, root, game_type_idx, game_idx, game_time = (0, '', [], None, 1, 1, None)):
        ret = True
        self.game_record_rt.game_state = Setting.GAME_NORMAL_REMOTE
        dict_all_game = self.dict_all_game_copy(self.dict_all_game)
        last_game_type = self.last_game_type
        game_record_rt = self.game_record_rt
        game_time = game_time
        self.game_time = game_time
        barcode_function = self.setting.barcode_function.get()
        player_num = self.player_num
        if player_num_cur != 0:
            player_num = player_num_cur
        self.player_num = player_num
        entry_user_name = self.entry_user_name
        if tourist_name != '':
            entry_user_name = tourist_name
        self.entry_user_name = entry_user_name
        list_player = self.list_player
        if list_player_cur != []:
            list_player = list_player_cur
        self.list_player = list_player
        main_obj = self
        life_value = self.life_value
        game_record_rt.game_blood = self.life_value
        game_record_rt.game_blood_right = self.life_value
        game_record_rt.game_blood_left = self.life_value
        if yanqian.yanqian():
            game_type = 'file'
            list_game_type = list(dict_all_game.keys())
            game_type_length = len(list_game_type)
            if game_type_idx > game_type_length - 1 or game_type_idx < 0:
                self.game_record_rt.game_state = Setting.GAME_NUMBER_ERROR
                return None
            type_index = None
            if type_index == 3:
                game_type = 'module'
            else:
                game_type_length -= 1
            game_index = game_idx
            list_game_path = []
            list_game = list(self.dict_all_game.values())[type_index]
            if game_index < 0 or game_index > len(list_game):
                self.game_record_rt.game_state = Setting.GAME_NUMBER_ERROR
                return None
            game_folder_name = None(self.dict_all_game.keys())[type_index]
            for j in range(game_index, len(list_game)):
                list_game_path.append('.//source//' + game_folder_name + '//' + list_game[j])
            
            for i in range(type_index + 1, game_type_length):
                list_game = self.dict_all_game[list_game_type[i]]
                for j in range(len(list_game)):
                    list_game_path.append('.//source//' + list_game_type[i] + '//' + list_game[j])
                
            
            game_time_pass = game_record_rt.get_game_time_pass()
            game_time = game_time - game_time_pass
            game_record_rt.game_time_left = game_time * 60
            if game_type == 'file':
                
                try:
                    if barcode_function and player_num > 0 and len(list_player) >= player_num:
                        self.gui_game = GuiGame(main_obj, life_value, list_game_path, barcode_function, game_time, list_player, root, **('last_root',))
                    elif player_num > 0:
                        list_player = []
                        for i in range(player_num):
                            list_player.append('')
                        
                        if entry_user_name == '':
                            list_player[0] = language.TOURIST + str(datetime.datetime.now().month) + str(datetime.datetime.now().day) + str(datetime.datetime.now().hour) + str(datetime.datetime.now().minute)
                        else:
                            list_player[0] = entry_user_name
                        self.gui_game = GuiGame(main_obj, life_value, list_game_path, barcode_function, game_time, list_player, root, **('last_root',))
                    else:
                        ret = messagebox.showerror(language.GAME_PLAYER, language.NO_SET, root, **('parent',))
                        ret = False
                except:
                    logger.error('{}', traceback.format_exc())
                    ret = False

            else:
                
                try:
                    if barcode_function and player_num > 0 and len(list_player) >= player_num:
                        self.gui_game = GuiGame(main_obj, life_value, list_game_path, barcode_function, game_time, list_player, root, **('last_root',))
                    elif player_num > 0:
                        list_player = []
                        for i in range(player_num):
                            list_player.append('')
                        
                        if entry_user_name == '':
                            list_player[0] = language.TOURIST + str(datetime.datetime.now().month) + str(datetime.datetime.now().day) + str(datetime.datetime.now().hour) + str(datetime.datetime.now().minute)
                        else:
                            list_player[0] = entry_user_name
                        self.gui_game = GuiGame(main_obj, life_value, list_game_path, barcode_function, game_time, list_player, root, **('last_root',))
                    else:
                        messagebox.showerror(language.GAME_PLAYER, language.NO_SET, root, **('parent',))
                        ret = False
                except:
                    logger.error('{}', traceback.format_exc())
                    ret = False

            logger.info('end of main start game')
            self.finish_game()
        else:
            ret = messagebox.showwarning(language.AUTHOR, language.UN_AUTHOR, root, **('parent',))
            ret = False
        return ret

    
    def game_start_thread(self, player_num_cur, game_type_idx, game_idx, game_time, play_name, game_level = (0, 1, 1, 10, None, 1)):
        logger.info('game_start_thread start')
        self.game_level = game_level
        self.start_button.focus_on('#66ffff')
        self.root.update()
        self.close_cur_activity()
        countdown = GuiCountDown(self, None, player_num_cur, play_name, game_type_idx, game_idx, game_time, 1, **('tourist_name', 'game_type_idx', 'game_idx', 'game_time', 'flag'))
        if not countdown.is_not_interrupt:
            self.finish_game()
            self.game_record_rt.running_to_obj = self
            logger.info('game_start_thread end')

    
    def finish_game_in_main_ui(self):
        self.game_record_rt.game_time_left = 0
        self.root.after(0, self.root_after_count_down)

    
    def finish_game_in_main_ui2(self):
        self.game_record_rt.reset(0, 0, 0, 0, self, **('running_to_obj',))
        self.list_player.clear()

    
    def main_canvas_keyboardTest(self, event, list_item, list_entry_item):
        print('main_canvas keycode:{0},char:{1},keysym:{2}'.format(event.keycode, event.char, event.keysym))
        if not event.keysym == 'F2' and self.gui_setting_opened:
            self.gui_setting_opened = True
            logger.info('keyboard click F2')
            self.close_cur_activity()
            gui.app_gui.AppUI(self, self.setting, self.debug, self.language_var)
            logger.info('keyboard click F2 function end')
        elif event.keysym == 'F3':
            self.finish_game_in_main_ui()
        elif event.keysym == 'F4':
            logger.info('game exit by f4')
            self.customized_function()
        for item in list_entry_item:
            if item.focus:
                str_char = '{0}'.format(event.char)
                print('str_char1', str_char)
                event = [
                    event.x,
                    event.y]
                item.input(str_char)

    
    def main_cavas_focus(self, event, list_canvas_button, list_canvas_entry):
        pass

