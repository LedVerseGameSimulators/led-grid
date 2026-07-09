# Source Generated with Decompyle++
# File: gui_game.pyc (Python 3.7)

import importlib
import json
import os
import datetime
import sys
import threading
import time
import traceback
from tkinter import messagebox
from loguru import logger
from game_play.Play import Play
from gui.gui_editor_game import EditorGame
from gui.gui_editor_game2 import EditorGame2
from gui.gui_game_result import GameResult
from gui.language import language
from led import led_control
from led.led_control_c import LedControl
from model.game import Game
from model.setting import Setting, Color
from audio_play import audio
from tourist_record.tourist_info import Tourist
from tourist_record.tourist_record_main import TouristRecord

class GuiGame:
    
    def get_video_path(self, music_folder, name):
        if name is not None and name != '' and name != 'None':
            return os.path.join(music_folder, name)
        return None

    
    def game_music_init(self, setting, music_folder, game):
        logger.info('game_music_init')
        music_game = self.cur_game_fragment
        music_game.ad_video = setting.game_idle_video.get()
        music_game.rule_introduce = self.get_video_path(music_folder, game.rule_introduce)
        music_game.bmg_video = self.get_video_path(music_folder, game.bmg_video)
        if music_game.bmg_video is None:
            music_game.bmg_video = setting.game_bg_audio.get()
        music_game.count_down = self.get_video_path(music_folder, game.count_down)
        music_game.red_tread = self.get_video_path(music_folder, game.red_tread)
        if music_game.red_tread is None:
            music_game.red_tread = setting.game_blood.get()
        music_game.clap_light = self.get_video_path(music_folder, game.clap_light)
        if music_game.clap_light is None:
            music_game.clap_light = None
        music_game.error_clap = self.get_video_path(music_folder, game.error_clap)
        if music_game.error_clap is None:
            music_game.error_clap = None
        music_game.correct = self.get_video_path(music_folder, game.correct)
        if music_game.correct is None:
            music_game.correct = None
        music_game.blue_tread = self.get_video_path(music_folder, game.blue_tread)
        if music_game.blue_tread is None:
            music_game.blue_tread = setting.game_scode.get()

    
    def play_music(self, ms_path, waitting, root = (False, None)):
        
        try:
            audio.Audio().play_bmg(ms_path)
            logger.info('play_music:{}', ms_path)
            if waitting:
                while audio.Audio().get_busy() and self.circle_game:
                    time.sleep(0.03)
                    root.update()
        except:
            logger.error(traceback.format_exc())


    
    def music(self, stage, waitting, root, loops = (False, None, -1)):
        logger.info('music')
        if stage == 'introduce':
            
            try:
                audio.Audio().play_bmg(self.cur_game_fragment.bmg_video, loops, **('loops',))
            except:

                pass

            logger.error(traceback.format_exc())

        elif stage == 'game_end':
            
            try:
                pass
            except:

                pass

            logger.error('game_end music{}', traceback.format_exc())

        elif stage == 'stop':
            audio.Audio().stop()

    
    def game_running(self, game_path, game_time, player_min_nums, barcode, life_value):
        module_name = game_path.split('.')[-1]
        if module_name == 'led':
            logger.info('in gui EditorGame')
            self.obj_module = EditorGame(self.parent, self, life_value, [], self.game_time, player_min_nums, self.last_root, game_path, **('last_root', 'game_unzip_dir'))
            logger.info('out of gui EditorGame')
        elif module_name == 'ledb':
            logger.info('in gui EditorGame2')
            self.obj_module = EditorGame2(self.parent, self, life_value, [], self.game_time, player_min_nums, self.last_root, game_path, **('last_root', 'game_unzip_dir'))
            logger.info('out of gui EditorGame2')
        else:
            logger.debug('play tennis running')
            module = importlib.import_module(f'''use_dll.{module_name}''')
            class_module = getattr(module, module_name)
            logger.info('in gui' + module_name)
            self.obj_module = class_module(self, life_value, barcode, game_time, player_min_nums, game_path)
            logger.info('out of gui ' + module_name)
        if self.last_module:
            self.last_root = self.last_module.ui.root
        if self.last_root and self.last_root != self.parent.root:
            self.last_root.destroy()
        self.last_module = self.obj_module

    
    def game_scode_rule(self, b_divide_person, b_divide_time, person_nums, time):
        scode = self.game_record_rt.game_scode
        battle_score = self.game_record_rt.game_info
        if battle_score:
            for value in battle_score[0]:
                scode += value
            
        if b_divide_person and person_nums != 0:
            scode /= person_nums
        if b_divide_time and time != 0:
            scode /= time
        return round(scode, 2)

    
    def db_operation_after_game(self, game_nums):
        game_time = self.main_obj.game_time
        tmp_list_custom_id = []
        list_participate = []
        for custom_id in self.list_phone_num:
            if custom_id != '':
                result = self.db.search_custom_by_phone(str(custom_id))
                
                try:
                    idx = tmp_list_custom_id.index(str(result[0][0]))
                    list_participate[idx] += 1
                except:

                    pass

                continue
                tmp_list_custom_id.append(str(result[0][0]))
                list_participate.append(1)
                continue

        self.list_phone_num = tmp_list_custom_id
        str_num = ''
        play_nums = 0
        for idx, num in enumerate(self.list_phone_num):
            if num != '':
                str_num += num
                str_num += ','
                play_nums += list_participate[idx]
        str_num = str_num[0:-1]
        rowcount = self.db.insert_player_group(str(play_nums), str_num)
        last_id_player = self.db.select_last_insert_id()
        self.player_group_id = last_id_player
        str_num = ''
        for num in self.list_game_name[:game_nums]:
            num = num
            str_num += num
            str_num += ','
        
        str_num = str_num[0:-1]
        rowcount = self.db.insert_game_group(str(game_nums), str(play_nums), str(self.setting.game_leval.get()), str_num)
        last_id_game = self.db.select_last_insert_id()
        self.game_group_id = last_id_game
        time_now = datetime.datetime.now()
        str_time = time_now.__format__('%Y-%m-%d %H:%M:%S')
        rowcount = self.db.insert_game_comsume(str_time, str(game_time), last_id_game, last_id_player)
        game_consume_id = self.db.select_last_insert_id()
        i = 0
        for custom_id in self.list_phone_num:
            time_consume = list_participate[i] * game_time
            result = self.db.search_custom_tb_by_id(str(custom_id))
            custom_time_left = float(result[0][-3]) - time_consume
            self.db.insert_custom_comsume(str(int(custom_id)), str(game_consume_id), str(list_participate[i]), str(game_time), str(time_consume))
            i += 1
        

    
    def update_custom_game_time(self, list_phone_num):
        tmp_list_custom_id = []
        list_participate = []
        game_time = self.main_obj.game_time
        for custom_id in list_phone_num:
            if custom_id != '':
                result = self.db.search_custom_by_phone(str(custom_id))
                
                try:
                    idx = tmp_list_custom_id.index(str(result[0][0]))
                    list_participate[idx] += 1
                except:

                    pass

                continue
                tmp_list_custom_id.append(str(result[0][0]))
                list_participate.append(1)
                continue

        i = 0
        for custom_id in tmp_list_custom_id:
            time_consume = list_participate[i] * game_time
            result = self.db.search_custom_tb_by_id(str(custom_id))
            custom_time_left = float(result[0][-3]) - time_consume
            self.db.update_custom_info_by_id(str(int(custom_id)), custom_time_left, **('time_left',))
            i += 1
        

    
    def game_result(self):
        if self.game_record_rt.game_time_left <= 0:
            logger.info('current game time out')
            player_num = len(self.player_list)
            game_time = self.main_obj.game_time
            if game_time == 0:
                game_time = 1
            self.player_group_id = 0
            scode = self.game_scode_rule(self.setting.game_scode_divide_person.get(), self.setting.game_scode_divide_time.get(), player_num, game_time)
            self.main_obj.last_game_score = scode
            if self.barcode and self.game_record_rt.game_state == Setting.GAME_NORMAL:
                logger.info('save data to remote db')
                
                try:
                    self.db_operation_after_game(self.game_nums)
                    self.db.insert_game_player_group(str(self.game_group_id), str(self.setting.game_leval.get()), str(game_time), self.str_time, str(self.player_group_id), str(scode))
                    result = self.db.search_game_result()
                    GameResult(self.parent, self.db, result, self.player_group_id, self.dir_name, game_time, len(self.list_phone_num), scode, self.barcode, self, **('cur_scode', 'barcode', 'parent_game_running'))
                except:
                    logger.error('{}', traceback.format_exc())

            else:
                logger.info('save data to local db')
                
                try:
                    tourist_record = TouristRecord()
                    tourist_record.connect()
                    tourist_record.create_table()
                    tourist = Tourist(self.player_list[0])
                    tourist.scode = scode
                    tourist_record.add(tourist)
                    result = tourist_record.search(100000, **('limit',))
                    tourist_record.close()
                    tourist_record.dispaly(self.parent, result, self.dir_name, game_time, len(self.player_list), scode, self, **('parent_game_running',))
                except:
                    logger.error('{}', traceback.format_exc())


    
    def start_game(self, setting, game_time, player_list, player_min_nums, barcode, life_value):
        self.list_phone_num = player_list.copy()
        self.game_time = game_time
        self.game_start_time = time.time()
        self.circle_game = True
        game_nums = 0
        dir_name = os.path.dirname(self.list_game[0])
        dir_name = os.path.basename(dir_name)
        circle_from = 0
        while self.circle_game:
            game_nums = circle_from
            list_game_tmp = self.list_game[circle_from:]
            for game_name in list_game_tmp:
                self.cur_game_name = game_name
                logger.info(game_name + ' running {}', game_nums)
                self.game_running(game_name, game_time, player_min_nums, barcode, life_value)
                logger.info(game_name + ' over')
                self.cur_game_name = None
                cur_time = time.time()
                time_pass = cur_time - self.game_start_time
                time_now = datetime.datetime.now()
                str_time = time_now.__format__('%Y-%m-%d %H:%M:%S')
                if self.game_record_rt.game_result == 0:
                    circle_from = game_nums
                    break
                else:
                    circle_from = 0
                game_nums += 1
                if not self.game_record_rt.game_time_left <= 0:
                    if not self.circle_game:
                        break
                    if not self.game_record_rt.game_time_left <= 0:
                        if not self.circle_game:
                            break
                        self.game_nums = game_nums
                        self.str_time = str_time
                        self.dir_name = dir_name
                        self.player_list = player_list
                        self.setting = setting
                        self.barcode = barcode
                        if self.game_record_rt.game_time_left <= 0:
                            logger.info('current game time out')
                            player_num = len(player_list)
                            game_time = self.main_obj.game_time
                            if game_time == 0:
                                game_time = 1
                            self.player_group_id = 0
                            scode = self.game_scode_rule(setting.game_scode_divide_person.get(), setting.game_scode_divide_time.get(), player_num, game_time)
                            self.main_obj.last_game_score = scode
                            if barcode and self.game_record_rt.game_state == Setting.GAME_NORMAL:
                                logger.info('save data to remote db')
                                
                                try:
                                    self.db_operation_after_game(game_nums)
                                    self.db.insert_game_player_group(str(self.game_group_id), str(self.setting.game_leval.get()), str(game_time), str_time, str(self.player_group_id), str(scode))
                                    result = self.db.search_game_result()
                                    GameResult(self.parent, self.db, result, self.player_group_id, dir_name, game_time, len(self.list_phone_num), scode, barcode, self, **('cur_scode', 'barcode', 'parent_game_running'))
                                except:
                                    logger.error('{}', traceback.format_exc())

                            else:
                                logger.info('save data to local db')
                                
                                try:
                                    tourist_record = TouristRecord()
                                    tourist_record.connect()
                                    tourist_record.create_table()
                                    tourist = Tourist(player_list[0])
                                    tourist.scode = scode
                                    tourist_record.add(tourist)
                                    result = tourist_record.search(100000, **('limit',))
                                    tourist_record.close()
                                    tourist_record.dispaly(self.parent, result, dir_name, game_time, len(player_list), scode, self, **('parent_game_running',))
                                except:
                                    logger.error('{}', traceback.format_exc())

                        else:
                            
                            try:
                                self.customized_function()
                            except:
                                logger.error('{}', traceback.format_exc())


    
    def get_hw_led_state_inc_wal(self, led_table_obj):
        if Setting.USE_SERIAL_HD:
            ret = led_control.get_led_state(None, led_table_obj.get_state_table(), None, None)
            if ret == 0:
                self.reopen_com()
            logger.debug('serial wall light draw')
            if self.setting.light.get():
                self.led_col_wall_light.get_wall_light_state(led_table_obj.get_wall_light_state_array(), self.setting.wall_light_layout_real)
            logger.debug('end')

    
    def draw_hw_led_color_inc_wal(self, led_table_obj):
        if Setting.USE_SERIAL_HD:
            ret = led_control.draw_led_color(None, led_table_obj.led_table)
            if ret == 0:
                self.reopen_com()
            logger.debug('serial wall light draw')
            if self.setting.light.get():
                self.led_col_wall_light.draw_wall_light_color(led_table_obj.get_wall_light_arr(), self.setting.wall_light_layout_real)
            logger.debug('end')
            logger.debug('serial wall screen draw')
            if self.setting.screen.get():
                self.led_col_wall_screen.update_wall_screen(led_table_obj.get_wall_screen_arr(), self.setting.wall_light_layout_real)
            logger.debug('end')

    
    def release_hw_led(self):
        if Setting.USE_SERIAL_HD:
            led_control.close_com()
            if self.led_col_wall_screen is not None:
                self.led_col_wall_screen.close_com()
            if self.led_col_wall_light is not None:
                self.led_col_wall_light.close_com()
            logger.info('release_hw_led')

    
    def init_hw_led(self):
        if Setting.USE_SERIAL_HD:
            self.led_col_wall_light = LedControl()
            serial_list_error = self.led_col_wall_light.init_com(self.setting.list_wall_com_info)
            for serial in serial_list_error:
                if self.last_root:
                    self.last_root.destroy()
                if self.parent.game_record_rt.game_state == Setting.GAME_NORMAL:
                    messagebox.showerror(language.SERIAL_OPEN_FAIL, serial)
                return False
            
            self.led_col_wall_screen = LedControl()
            serial_list_error = self.led_col_wall_screen.init_com(self.setting.list_screen_com_info)
            for serial in serial_list_error:
                if self.last_root:
                    self.last_root.destroy()
                if self.parent.game_record_rt.game_state == Setting.GAME_NORMAL:
                    messagebox.showerror(language.SERIAL_OPEN_FAIL, serial)
                return False
            
            serial_list_error = led_control.init_com(self.setting.list_com_info)
            led_control.init_layout(self.setting.type, self.led_row, self.led_col, self.setting.floor_layout_coors_no_use)
            for serial in serial_list_error:
                if self.last_root:
                    self.last_root.destroy()
                if self.parent.game_record_rt.game_state == Setting.GAME_NORMAL:
                    messagebox.showerror(language.SERIAL_OPEN_FAIL, serial)
                return False
            
        logger.info('init_hw_led')
        return True

    
    def __init__(self, parent, life_value, list_game, barcode, game_time, player_list, last_root = (None,)):
        self.game_nums = 0
        player_min_nums = parent.player_num
        self.game_level = parent.game_level
        self.cur_game_fragment = Game('none')
        self.last_root = last_root
        self.last_module = None
        self.game_record_rt = parent.game_record_rt
        self.last_time = 0
        self.life_value = life_value
        self.setting = parent.setting
        self.led_col = None
        self.parent = parent
        self.main_obj = parent
        self.db = parent.db
        self.cur_game_name = None
        self.led_col_wall_light = None
        self.led_col_wall_screen = None
        self.led_row = int(self.setting.value_high.get())
        self.led_col = int(self.setting.value_width.get())
        self.life_cal = None
        self.list_game = list_game
        self.list_game_name = []
        for game_path in self.list_game:
            self.list_game_name.append(os.path.basename(game_path))
        
        wall_corner_line_start = self.setting.corner_line_start.get()
        self.wall_corner_line_start = wall_corner_line_start
        self.play = None
        if not self.init_hw_led():
            self.game_record_rt.game_state = Setting.GAME_HW_ERROR
            self.parent.finish_game_in_main_ui2()
            logger.warning('init_hw_led false')
            return None
        if None.game_record_rt.game_state == Setting.GAME_NORMAL and barcode and self.game_record_rt.game_time_start == 0:
            self.update_custom_game_time(player_list.copy())
        self.game_record_rt.start_game_time()
        self.start_game(self.setting, game_time, player_list, player_min_nums, barcode, life_value)
        self.finish_game()

    
    def close_last_root(self):
        if self.last_root:
            self.last_root.destroy()

    
    def customized_function(self):
        self.circle_game = False
        self.play_running_stop()

    
    def finish_game(self):
        self.release_hw_led()
        self.circle_game = False
        audio.Audio().stop()
        if self.last_root:
            self.last_root.destroy()
        if self.last_module:
            self.last_module.ui.root.destroy()
        logger.info('finish game')

    
    def play_running(self, partial_update, game, dict_group, game_folder_path, led_table_obj, root, play = (None, None, None)):
        setting = self.setting
        self.play = play
        if self.play:
            self.play.callback = partial_update
        self.game_music_init(setting, game_folder_path, game)
        if game.play_order:
            loops = 0
        else:
            loops = -1
        self.music('introduce', True, root, loops)
        if game.play_order:
            self.play.running(dict_group)
        else:
            self.play.running_by_blue(dict_group)
        self.music('stop')
        logger.info('play_running end')

    
    def play_running_stop(self):
        if self.play:
            self.play.stop_running()
            logger.info('editor game running stop')

    
    def reopen_com(self):
        if Setting.USE_SERIAL_HD:
            logger.info('start reopen com')
            led_control.close_com()
            serial_list_error = led_control.init_com(self.setting.list_com_info)
            led_control.init_layout(self.setting.type, self.led_row, self.led_col, self.setting.floor_layout_coors_no_use)
            logger.info('end reopen com')


