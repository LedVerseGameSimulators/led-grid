# Source Generated with Decompyle++
# File: life_value_calculation.pyc (Python 3.7)

import shelve
import time
from audio_play import audio
from loguru import logger
from model.setting import Color, Setting
from model_in.led_group import LedGroup

class LifeValueCalculation:
    ALL_LIFE_VALUE = 10
    ONE_LIFE_VALUE = 1
    ONE_SCODE_VALUE = 1
    
    def __init__(self, row, col, one_life_value, table_state, table_color, audio_name_sub, audio_name_add, game_name, all_life_value, scode_init, scode_left, scode_right = (1, None, None, './audio/bomb.mp3', './audio/prompt.mp3', None, 10, 0, 0, 0)):
        time_now = time.time()
        self.table_tread_time = (lambda _iter_ = None: [ [
time_now] * col for _ in _iter_ ])(range(row))
        self.table_tread_duration_time = (lambda _iter_ = None: [ [
0] * col for _ in _iter_ ])(range(row))
        self.arr_count_between_time = [
            10] * (row + col)
        self.table_count_time = (lambda _iter_ = None: [ [
1] * col for _ in _iter_ ])(range(row))
        self.row = row
        self.col = col
        LifeValueCalculation.ALL_LIFE_VALUE = all_life_value
        
        try:
            f = shelve.open('./setting/debug_parameter')
            self.duration_time = float(f.get('tread_red_time'))
            self.TIME = float(f.get('life_value_count_time'))
            f.close()
        except:
            self.duration_time = 0.1
            self.TIME = 1

        logger.warning('踩红灯持续时间{}, 掉血时间间隔{}', self.duration_time, self.TIME)
        self.one_life_value = one_life_value
        self.table_state = table_state
        self.table_color = table_color
        self.audio_name_sub = audio_name_sub
        self.audio_name_add = audio_name_add
        self.life_value = LifeValueCalculation.ALL_LIFE_VALUE
        self.scode_value = scode_init
        self.last_value_dec_time = time.time()
        self.life_value_left = 0
        self.life_value_right = 0
        self.scode_value_left = scode_left
        self.scode_value_right = scode_right

    
    def calculation_old(self, life_value, flag_one, table_state, row, col = ((), ())):
        if row[0] < 1 and row[1] > self.row and col[0] < 1 or col[1] > self.col:
            return None
        time_now = None.time()
        for i in range(row[0] - 1, row[1]):
            for j in range(col[0] - 1, col[1]):
                time_last = self.table_tread_time[i][j]
                time_bettwn = time_now - time_last
                if table_state[i][j] and time_bettwn > self.TIME:
                    life_value -= self.one_life_value
        

    
    def calculation(self, life_value, color, table_state, table_color, audio_name, state_update = ('./audio/bomb.mp3', None)):
        time_now = time.time()
        if state_update is None:
            for i in range(self.row):
                for j in range(self.col):
                    time_last = self.table_tread_time[i][j]
                    time_bettwn = time_now - time_last
                    if table_state[i][j] and table_color[i][j] in color and time_bettwn > self.TIME:
                        life_value -= self.one_life_value
                        self.table_tread_time[i][j] = time_now
                        audio.Audio().play(audio_name)
            
        else:
            for i in range(self.row):
                for j in range(self.col):
                    time_last = self.table_tread_time[i][j]
                    time_bettwn = time_now - time_last
                    if table_state[i][j] and table_color[i][j] in color and time_bettwn > self.TIME and state_update[i][j]:
                        life_value -= self.one_life_value
                        self.table_tread_time[i][j] = time_now
                        audio.Audio().play(audio_name)
            
        return life_value

    
    def calculation_one_second_snake(self, life_value, color, table_state, table_color, audio_name, time_passed, min_time = ('./audio/snake/bomb.mp3', 0, None)):
        if min_time is not None:
            min_time = min_time
        else:
            min_time = self.duration_time
        time_now = time.time()
        time_bettwn = time_now - self.last_value_dec_time
        for i in range(self.row):
            for j in range(self.col):
                if table_state[i][j] and table_color[i][j] in color:
                    self.table_tread_duration_time[i][j] += time_passed
                else:
                    self.table_tread_duration_time[i][j] = 0
                if self.table_tread_duration_time[i][j] > min_time and time_bettwn > self.TIME:
                    life_value -= self.one_life_value
                    audio.Audio().play(audio_name)
                    self.last_value_dec_time = time_now
                    return life_value
            
        
        return life_value

    
    def calculation_editor_group(self, group_dict, cur_time, time_pass, table_state, table_color, red_table, green_table, safe_table, audio_name, audio_scode, group_blink, group_blink_2, hidden_tread_show, hidn_tread_show_time = (None, None, None, None, None, 0)):
        for key, group in group_dict.items():
            if cur_time < cur_time:
                if cur_time < group.end_time_sec:
                    pass
                else:
                    group.start_time_sec
                for coors in group.start_member.copy():
                    i = coors[0]
                    j = coors[1]
                    if table_state[i][j]:
                        if red_table[i][j]:
                            if green_table[i][j] and group.color == Color.RED and self.table_count_time[i][j] > self.TIME:
                                self.life_value -= self.one_life_value
                                self.scode_value -= self.ONE_SCODE_VALUE
                                audio.Audio().play(audio_name)
                                self.table_count_time[i][j] = 0
                                if group_blink is not None:
                                    group_blink.add_led_blink([
                                        (i, j)])
                                elif group.color == table_color[i][j]:
                                    self.scode_value += self.ONE_SCODE_VALUE
                                    group.start_member.remove(coors)
                                    audio.Audio().play(audio_scode)
                                    if green_table[i][j] or group_blink_2 is not None:
                                        group_tmp = LedGroup([
                                            (i, j)], group.color, **('color',))
                                        group_blink_2.append(group_tmp)
                                    elif safe_table[i][j] and hidden_tread_show is not None:
                                        group_tmp = LedGroup([
                                            (i, j)], group.color, hidn_tread_show_time, True, **('color', 'life_period', 'is_living'))
                                        hidden_tread_show.append(group_tmp)
                                        continue
                                        self.table_count_time[i][j] += time_pass
                
        

    
    def calculation_one_second_250513(self, life_value, color, table_state, table_color, audio_name, audio_scode, time_passed, min_time, group_blink, no_score_color = (None, None, 0, None, None, [])):
        if min_time is not None:
            min_time = min_time
        else:
            min_time = self.duration_time
        time_now = time.time()
        time_bettwn = time_now - self.last_value_dec_time
        for i in range(self.row):
            for j in range(self.col):
                if table_color[i][j] == Color.TEST_COLOR:
                    logger.debug('state{}', table_state[i][j])
                if table_state[i][j] and table_color[i][j] in color:
                    self.table_tread_duration_time[i][j] += time_passed
                else:
                    self.table_tread_duration_time[i][j] = 0
                self.table_count_time[i][j] += time_passed
                if table_state[i][j] and table_color[i][j] not in no_score_color:
                    self.scode_value += self.ONE_SCODE_VALUE
                    audio.Audio().play(audio_scode)
                if self.table_tread_duration_time[i][j] > min_time and self.table_count_time[i][j] > self.TIME:
                    self.life_value -= self.one_life_value
                    self.scode_value -= self.ONE_SCODE_VALUE
                    audio.Audio().play(audio_name)
                    self.last_value_dec_time = time_now
                    self.table_count_time[i][j] = 0
                    if group_blink is not None:
                        group_blink.add_led_blink([
                            (i, j)])
                return None

    
    def calculation_one_second_wall_light_dict_group(self, arr_state, audio_name, dict_group, total_pass = ('./audio/bomb.mp3', None, 0)):
        pass
