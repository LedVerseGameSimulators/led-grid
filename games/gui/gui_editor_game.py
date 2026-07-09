# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: gui_editor_game.py
import datetime, os.path, sys, time, traceback
from functools import partial
from loguru import logger
from audio_play import audio
import game_play.Play as Play
from game_play.game_util import GameUtil
from gui.gui_ui import GuiUI
from game_play.led_blink import LedBlinkGroup
from game_play.life_value_calculation import LifeValueCalculation
from model.setting import Setting, Color
from model_in.led_group import LedGroup

class EditorGame:

    def play_running(self, game_unzip_dir, setting, partial_update_ui):
        led_table_obj = self.ui.led_table
        self.game_util.unzipfile(game_unzip_dir)
        logger.info("game_unzip_dir")
        game_unzip_dir = os.path.splitext(game_unzip_dir)[0]
        self.cur_game_name = game_unzip_dir
        self.ui.update_game_name_ui(os.path.basename(game_unzip_dir).split(".")[0])
        tmp_partial_update = partial(self.callback_for_end_game_fragment)
        try:
            for game_folder in os.listdir(game_unzip_dir):
                logger.info(game_folder)
                if self.circle_game:
                    game, dict_group = self.game_util.read_game_and_group(game_unzip_dir, game_folder, setting)
                    self.cur_game_time = self.game_util.get_max_end_time_in_all_group(dict_group)
                    color_tmp = game.safe_color
                    self.cover_color = (Color.GREEN, color_tmp, Color.RED)
                    self.no_score_color = (Color.GREEN, color_tmp, Color.RED, Color.BLACK)
                    self.ui.led_table.safe_color = color_tmp
                    if game.cover_action:
                        self.cover_action = "prompt"
                    else:
                        self.cover_action = "disappear"
                    game_folder_path = game_unzip_dir + "/" + game_folder
                    self.parent_game_running.play_running(partial_update_ui, game, dict_group, game_folder_path, led_table_obj,
                      (self.ui.root), play=(self.play))
                    if self.circle_game:
                        if self.game_record_rt.game_result == 0:
                            self.life_cal.life_value = 1
                            game_end, dict_group_end, game_end_dir = self.game_util.read_game_parameter_game_frag(os.path.join(game_unzip_dir + "/" + game_folder, "game_file"), game.clap_light, setting)
                        else:
                            game_end, dict_group_end, game_end_dir = self.game_util.read_game_parameter_game_frag(os.path.join(game_unzip_dir + "/" + game_folder, "game_file"), game.game_accomplished, setting)
                        if game_end is not None and dict_group_end is not None:
                            self.cur_game_time = self.game_util.get_max_end_time_in_all_group(dict_group_end)
                            self.parent_game_running.play_running(tmp_partial_update, game_end, dict_group_end, game_end_dir, led_table_obj,
                              (self.ui.root), play=(self.play))

        except:
            logger.error(traceback.format_exc())

        self.update_draw_led_table_end_of_play()
        self.game_util.remove_unzipfile(game_unzip_dir)
        logger.info("EditorGame end play_running")

    def screen_mouse_click_state_get(self):
        coors_click = self.ui.led_table.led_coors_click
        self.ui.led_table.get_state_table()[coors_click[0][0]][coors_click[0][1]] = coors_click[1]
        coors_click = self.ui.led_table.led_coors_click_wall
        self.ui.led_table.get_wall_light_state_array()[coors_click[0][1]] = coors_click[1]

    def update_draw_led_table_end_of_play(self):
        try:
            self.game_record_rt.game_scode = self.life_cal.scode_value
            self.game_record_rt.game_blood = self.life_cal.life_value
            self.ui.led_table.clear_led_table()
            self.update_hw_led_new(self.game_record_rt)
        except:
            logger.error("update_draw_led_table_end_of_play{}", traceback.format_exc())

    def get_group_state(self, group_member):
        table_state = self.ui.led_table.table_state
        for coors in group_member:
            if table_state[coors[0]][coors[1]]:
                return True

        return False

    def draw_tread_short_stay(self, time_pass):
        for group in self.list_hidden_tread_group.copy():
            if group.is_living:
                group.vary(time_pass)
                group.draw(self.ui.led_table.tread_short_stay, group.color)
            else:
                self.list_hidden_tread_group.remove(group)

    def draw_code_group(self, time_pass):
        color_table = self.ui.led_table.led_table
        last_trigger_span = self.ui.led_table.last_trigger_span
        if not len(self.list_group_breath) > 0 or len(self.list_hidden_coors) or len(self.list_hidden_group):
            group = self.list_group_breath[0]
            group_state = self.get_group_state(group.member)
            if group_state and group.trigger_span_tm > self.trigger_span:
                audio.Audio().play(self.parent_game_running.cur_game_fragment.red_tread)
                group.trigger_span_tm = 0
                self.life_cal.scode_value -= self.prompt_cost
                group = LedGroup((group.member.copy()), color=(group.color))
                self.list_group_blink.append(group)
                print(self.list_hidden_coors)
                print(self.list_hidden_colors)
                for idx in range(len(self.list_hidden_coors) - 1, -1, -1):
                    coors = self.list_hidden_coors[idx]
                    if not self.table_cover_show[coors[0]][coors[1]]:
                        color_tmp = self.list_hidden_colors[idx]
                        group = LedGroup([(coors[0], coors[1])], color=color_tmp, life_period=(self.prompt_time), is_living=True)
                        self.list_hidden_group.append(group)
                        self.list_hidden_coors.pop(idx)
                        self.list_hidden_colors.pop(idx)
                        self.table_cover_show[coors[0]][coors[1]] = True

        else:
            group.breath(time_pass)
            group.draw(color_table, group.breath_color)
        for group in self.list_hidden_group.copy():
            group_state = self.get_group_state(group.member)
            print(f"hidden group{group.member}")
            if group_state:
                self.list_hidden_group.remove(group)
                print(f"hidden coors remove{group.member}")
                blink_group = LedGroup((group.member.copy()), color=(group.color))
                self.list_group_blink.append(blink_group)
                for coors in group.member:
                    self.table_cover_show[coors[0]][coors[1]] = False

            elif group.is_living:
                group.vary(time_pass)
                group.draw(color_table, group.color)
            else:
                for coors in group.member:
                    self.table_cover_show[coors[0]][coors[1]] = False

                self.list_hidden_group.remove(group)

        for group_blink in self.list_group_blink.copy():
            if group_blink.is_exist:
                group_blink.blink(time_pass)
                group_blink.draw(color_table, group_blink.blink_color)
            else:
                self.list_group_blink.remove(group_blink)

    def find_cover_color_coors(self, list_group, time_cur, coors_list, coors_list_red):
        o_led_table = self.ui.led_table
        time_threshold = self.blue_hide_max_time + 5
        for group in list_group:
            if group.type == Setting.FLOOR_LIGHT and group.speed == 0:
                if group.start_time_sec + time_threshold < time_cur < group.end_time_sec:
                    if group.color in self.cover_color:
                        if group.color == Color.RED or group.color == Color.GREEN:
                            for cell in group.start_member:
                                i = round(cell[0])
                                j = round(cell[1])
                                if o_led_table.plus_table[i][j] is not None or o_led_table.deduct_table[i][j]:
                                    coors_list_red.append((i, j))

            else:
                for cell in group.start_member:
                    i = round(cell[0])
                    j = round(cell[1])
                    if o_led_table.plus_table[i][j] is not None or o_led_table.deduct_table[i][j]:
                        coors_list.append((i, j))

    def color_cover_over_times_prompt(self, dict_group, time_cur):
        o_led_table = self.ui.led_table
        time_threshold = self.blue_hide_max_time + 5
        list_group = dict_group.values()
        self.list_hidden_coors.clear()
        self.list_hidden_colors.clear()
        coors_list = []
        coors_list_red = []
        self.find_cover_color_coors(list_group, time_cur, coors_list, coors_list_red)
        for group in list_group:
            if group.type == Setting.FLOOR_LIGHT and group.speed == 0:
                if group.start_time_sec + time_threshold < time_cur < group.end_time_sec:
                    if group.color in Color.PLUS_ARR:
                        for cell in group.start_member.copy():
                            i = cell[0]
                            j = cell[1]
                            if not (self.table_cover_show[i][j] or o_led_table.green_table[i][j]):
                                if o_led_table.safe_table[i][j] or o_led_table.red_table[i][j]:
                                    if cell in coors_list:
                                        self.list_hidden_coors.append(cell)
                                        self.list_hidden_colors.append(group.color)
                                if cell in coors_list_red:
                                    group.start_member.remove(cell)

    def color_cover_over_times_disappear(self, dict_group, time_cur):
        o_led_table = self.ui.led_table
        time_threshold = self.blue_hide_max_time
        list_group = dict_group.values()
        coors_list = []
        coors_list_red = []
        self.find_cover_color_coors(list_group, time_cur, coors_list, coors_list_red)
        coors_list_all = coors_list + coors_list_red
        for group in list_group:
            if group.type == Setting.FLOOR_LIGHT and group.speed == 0:
                if group.start_time_sec + time_threshold < time_cur < group.end_time_sec:
                    if group.color in Color.PLUS_ARR:
                        for cell in group.start_member.copy():
                            i = round(cell[0])
                            j = round(cell[1])
                            if o_led_table.red_table[i][j] or o_led_table.green_table[i][j] or o_led_table.safe_table[i][j]:
                                if cell in coors_list_all:
                                    group.start_member.remove(cell)

    def calculation_editor_group_scode(self, group_dict, cur_time, time_pass):
        led_table = self.ui.led_table
        table_state = led_table.table_state
        red_table = led_table.red_table
        green_table = led_table.green_table
        safe_table = led_table.safe_table
        audio_name = self.parent_game_running.cur_game_fragment.red_tread
        audio_scode = self.parent_game_running.cur_game_fragment.blue_tread
        group_blink = self.led_blink_group
        hidden_tread_show = self.list_hidden_tread_group
        hidn_tread_show_time = self.hidn_tread_show_time
        for key, group in group_dict.items():
            if group.type == Setting.FLOOR_LIGHT:
                if group.start_time_sec < cur_time < group.end_time_sec:
                    if group.color == Color.RED:
                        for coors in group.start_member.copy():
                            i = coors[0]
                            j = coors[1]
                            if table_state[i][j] and not green_table[i][j]:
                                if cur_time - self.life_cal.table_count_time[i][j] > self.life_cal.TIME:
                                    self.life_cal.life_value -= self.life_cal.one_life_value
                                    self.life_cal.scode_value -= self.life_cal.ONE_SCODE_VALUE
                                    audio.Audio().play(audio_name)
                                    self.life_cal.table_count_time[i][j] = cur_time
                                    group_blink.add_led_blink([(i, j)])

                    elif group.color == Color.DEDUCT_COLOR:
                        for coors in group.start_member.copy():
                            i = coors[0]
                            j = coors[1]
                            if table_state[i][j]:
                                if not (green_table[i][j]) and not (red_table[i][j]): self.life_cal.scode_value -= self.life_cal.ONE_SCODE_VALUE
                                audio.Audio().play(audio_name)
                                if safe_table[i][j]:
                                    if cur_time - self.life_cal.table_count_time[i][j] > self.life_cal.TIME:
                                        self.life_cal.table_count_time[i][j] = cur_time
                                        group_tmp = LedGroup([(i, j)], color=(group.color), life_period=hidn_tread_show_time,
                                          is_living=True)
                                        hidden_tread_show.append(group_tmp)
                                group.start_member.remove(coors)
                                group_blink.add_led_blink([(i, j)])

                    elif group.color in Color.PLUS_ARR:
                        for coors in group.start_member.copy():
                            i = coors[0]
                            j = coors[1]
                            if table_state[i][j]:
                                if not (green_table[i][j]) and not (red_table[i][j]): self.life_cal.scode_value += self.life_cal.ONE_SCODE_VALUE
                                group.start_member.remove(coors)
                                audio.Audio().play(audio_scode)
                                if safe_table[i][j]:
                                    group_tmp = LedGroup([(i, j)], color=(group.color), life_period=hidn_tread_show_time,
                                      is_living=True)
                                    hidden_tread_show.append(group_tmp)

    def callback_in_every_frame(self, parent, dict_group, time_pass, total_pass):
        try:
            led_table = self.ui.led_table
            if self.cover_action == "disappear":
                self.color_cover_over_times_disappear(dict_group, total_pass)
            else:
                self.color_cover_over_times_prompt(dict_group, total_pass)
            cur_game_fragment = self.parent_game_running.cur_game_fragment
            try:
                self.calculation_editor_group_scode(dict_group, total_pass, time_pass)
                if (self.setting.screen.get() or self.setting.light.get)():
                    self.life_cal.calculation_one_second_wall_light_dict_group((led_table.get_wall_light_state_array()), audio_name=(cur_game_fragment.blue_tread),
                      dict_group=dict_group,
                      total_pass=total_pass)
                else:
                    if self.setting.screen.get():
                        self.life_cal.calculation_one_second_screen_light_dict_group((led_table.get_wall_light_state_array()), (led_table.get_wall_screen_arr()),
                          audio_name=(cur_game_fragment.red_tread),
                          audio_scode=(cur_game_fragment.blue_tread),
                          time_passed=time_pass,
                          dict_group=dict_group,
                          total_pass=total_pass)
            except:
                logger.error(traceback.format_exc())

            self.draw_tread_short_stay(time_pass)
            led_table.redraw_led_table_default(line=(self.setting.corner_line_start.get()), draw_canvas=False)
            self.draw_code_group(time_pass)
            self.led_blink_group.group_blink(time_pass)
            self.game_record_rt.game_scode = self.life_cal.scode_value
            self.game_record_rt.game_blood = self.life_cal.life_value
            self.game_record_rt.game_time_left -= time_pass
            self.update_hw_led_new(self.game_record_rt)
            if self.life_cal.life_value <= 0 or total_pass > self.cur_game_time or self.game_record_rt.game_time_left <= 0:
                self.game_record_rt.game_scode = self.life_cal.scode_value
                self.game_record_rt.game_blood = self.life_cal.life_value
                if self.life_cal.life_value <= 0:
                    self.game_record_rt.game_result = 0
                else:
                    if total_pass > self.cur_game_time:
                        self.game_record_rt.game_result = 1
                    else:
                        self.game_record_rt.game_result = 2
                self.ui.led_table.clear_led_table()
                self.update_hw_led_new(self.game_record_rt)
                logger.info("editor game callback over")
                return False
            return True
        except:
            logger.error(traceback.format_exc())
            return False

    def callback_for_end_game_fragment(self, parent, dict_group, time_pass, total_pass):
        try:
            led_table = self.ui.led_table
            cur_game_fragment = self.parent_game_running.cur_game_fragment
            led_table.redraw_led_table_default(line=(self.setting.corner_line_start.get()), draw_canvas=False)
            self.led_blink_group.group_blink(time_pass)
            self.game_record_rt.game_time_left -= time_pass
            self.update_hw_led_new(self.game_record_rt)
            if total_pass > self.cur_game_time or self.game_record_rt.game_time_left <= 0:
                self.game_record_rt.game_scode = self.life_cal.scode_value
                self.game_record_rt.game_blood = self.life_cal.life_value
                self.ui.led_table.clear_led_table()
                self.update_hw_led_new(self.game_record_rt)
                logger.info("editor game(end game frag) callback over")
                return False
            return True
        except:
            logger.error(traceback.format_exc())
            return False

    def screen_mouse_event(self, event, root):
        full_screen = not self.full_screen
        root.attributes("-fullscreen", full_screen)

    def update_hw_led_new(self, game_record):
        try:
            if Setting.USE_SERIAL_HD:
                self.parent_game_running.draw_hw_led_color_inc_wal(self.ui.led_table)
                self.ui.update_ui(game_record)
                self.parent_game_running.get_hw_led_state_inc_wal(self.ui.led_table)
            else:
                self.ui.update_ui(game_record)
                self.screen_mouse_click_state_get()
        except:
            logger.error(traceback.format_exc())

    def __init__(self, parent, parent_last, life_value, list_game, game_time, player_min_num, last_root=None, game_unzip_dir=''):
        logger.info("gui editor game")
        self.game_util = GameUtil()
        self.game_time = game_time
        self.game_start_time = time.time()
        self.game_record_rt = parent.game_record_rt
        self.game_record_rt.running_to_obj = self
        self.main_obj = parent
        self.last_time = 0
        self.life_value = life_value
        self.game_level = parent.game_level
        self.setting = parent.setting
        self.led_col = None
        self.parent = parent
        self.parent_game_running = parent_last
        self.db = parent.db
        self.cur_game_name = None
        self.cur_game_fragment = None
        self.led_col_wall_light = None
        self.led_col_wall_screen = None
        self.led_row = int(self.setting.value_high.get())
        self.led_col = int(self.setting.value_width.get())
        self.blue_hide_max_time = self.setting.blue_hide_max_time.get()
        self.life_cal = None
        self.list_game = list_game
        self.list_game_name = []
        for game_path in self.list_game:
            self.list_game_name.append(os.path.basename(game_path))

        self.circle_game = True
        wall_light_arr_len = len(self.setting.wall_light_table)
        row = int(self.setting.value_high.get())
        col = int(self.setting.value_width.get())
        wall_line = self.setting.corner_line_start.get()
        self.ui = GuiUI(self, life_value, row, col, wall_light_arr_len, wall_line, mode=0)
        self.led_blink_group = LedBlinkGroup(self.ui.led_table.led_table, Color.RED_BLINK, Color.BLACK)
        self.list_hidden_group = []
        self.list_hidden_tread_group = []
        self.list_group_blink = []
        self.list_hidden_coors = []
        self.list_hidden_colors = []
        self.list_group_breath = []
        self.table_cover_show = [[False] * col for _ in range(row)]
        self.trigger_span = 1
        self.prompt_cost = self.setting.hidden_prompt_score.get()
        self.prompt_time = self.setting.hidden_show_time.get()
        self.hidn_tread_show_time = self.setting.hidn_tread_show_time.get()
        group_tmp = LedGroup([(0, col - 1)], color=(self.ui.color_hex_str2int_arr(self.setting.hidden_prompt_breath_color.get())))
        self.list_group_breath.append(group_tmp)
        audio_blood_path = self.setting.game_blood.get()
        audio_scode_path = self.setting.game_scode.get()
        self.cover_action = "disappear"
        if audio_blood_path == "":
            audio_blood_path = "./audio/bomb.mp3"
        if audio_scode_path == "":
            audio_scode_path = "./audio/prompt.mp3"
        self.life_cal = LifeValueCalculation((self.led_row), (self.led_col), audio_name_sub=audio_blood_path,
          audio_name_add=audio_scode_path,
          all_life_value=life_value,
          scode_init=(self.game_record_rt.game_scode))
        partial_update = partial(self.callback_in_every_frame)
        self.play = Play((self.ui.led_table), (self.setting), partial_update, game_level=(self.game_level))
        self.play_running(game_unzip_dir, self.setting, partial_update)

    def customized_function(self):
        self.circle_game = False
        audio.Audio().stop()
        self.parent_game_running.customized_function()
        self.play.is_game_living = False
        logger.info("editor ui close")

# okay decompiling /games/climb/climb_source_code/gui/gui_editor_game.pyc
