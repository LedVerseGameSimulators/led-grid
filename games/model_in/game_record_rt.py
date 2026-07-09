# Source Generated with Decompyle++
# File: game_record_rt.pyc (Python 3.7)

import time
from model.setting import Setting

class GameRecordRT:
    
    def __init__(self):
        self.game_time_pass = 0
        self.game_time_start = 0
        self.game_time_left = 0
        self.game_scode = 0
        self.game_scode_left = 0
        self.game_scode_right = 0
        self.game_blood = 0
        self.game_blood_left = 0
        self.game_blood_right = 0
        self.game_result = 2
        self.game_info = None
        self.game_state = Setting.GAME_IDLE
        self.running_to_obj = None
        self.running_to_flag = 0

    
    def reset(self, game_time_pass, game_scode, game_scode_left, game_scode_right, running_to_obj = (None, None, None, None, None)):
        self.game_time_start = 0
        if game_time_pass is not None:
            self.game_time_pass = game_time_pass
        if game_scode is not None:
            self.game_scode = game_scode
        if game_scode_left is not None:
            self.game_scode_left = game_scode_left
        if game_scode_right is not None:
            self.game_scode_right = game_scode_right
        self.game_result = 2
        self.game_time_left = 0
        self.game_info = None
        self.running_to_obj = running_to_obj

    
    def get_game_time_pass(self):
        if self.game_time_start > 0:
            self.game_time_pass = (time.time() - self.game_time_start) / 60
        else:
            self.game_time_pass = 0
        return self.game_time_pass

    
    def start_game_time(self):
        if self.game_time_start == 0:
            self.game_time_start = time.time()


