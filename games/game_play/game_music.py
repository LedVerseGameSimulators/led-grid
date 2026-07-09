# Source Generated with Decompyle++
# File: game_music.pyc (Python 3.7)

import os
import sys
import time
import traceback
from loguru import logger
from audio_play import audio

class GameMusic:
    
    def music_close(self):
        self.circle_game = False
        audio.Audio().stop()

    
    def waiting_running(self):
        while audio.Audio().get_busy() and self.circle_game:
            time.sleep(0.01)
            if self.root:
                self.root.update()
            return None

    
    def waitting_music_end(self, waitting):
        if waitting:
            self.waiting_running()

    
    def get_video_path(self, music_folder, name):
        if name is not None and name != '' and name != 'None':
            return os.path.join(music_folder, name)
        return None

    
    def music(self, stage, waitting = (False,)):
        if stage == 'introduce':
            
            try:
                audio.Audio().play_bmg(self.rule_introduce)
                self.waitting_music_end(waitting)
                audio.Audio().queue(self.count_down)
                self.waitting_music_end(waitting)
                audio.Audio().play_bmg(self.bmg_video, -1, **('loops',))
            logger.error(traceback.format_exc())

        elif stage == 'game_success':
            
            try:
                audio.Audio().play_bmg(self.game_accomplished, 0, **('loops',))
                self.waitting_music_end(waitting)
            print('audio except')

        elif stage == 'stop':
            audio.Audio().stop()

    
    def __int__todo(self, root, setting, music_folder, game, init_music = (None,)):
        self.circle_game = True
        self.root = root
        music_game = self
        if init_music:
            self.game_introduce = init_music.game_introduce
            self.game_start = init_music.game_start
            self.game_bgm = init_music.game_bgm
            self.game_pass = init_music.game_pass
            self.game_failure = init_music.game_failure
        else:
            music_game.rule_introduce = self.get_video_path(music_folder, game.rule_introduce)
            if music_game.rule_introduce is None:
                music_game.rule_introduce = setting.game_name.get()
            music_game.bmg_video = self.get_video_path(music_folder, game.bmg_video)
            if music_game.bmg_video is None:
                music_game.bmg_video = setting.game_bg_audio.get()
            music_game.count_down = self.get_video_path(music_folder, game.count_down)
            if music_game.count_down is None:
                music_game.count_down = setting.game_start_video.get()
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
            music_game.game_accomplished = self.get_video_path(music_folder, game.game_accomplished)
            if music_game.game_accomplished is None:
                music_game.game_accomplished = setting.game_pass.get()
            music_game.clap_light = self.get_video_path(music_folder, game.clap_light)
            if music_game.clap_light is None:
                music_game.clap_light = setting.game_failure.get()

    
    def __init__(self, root, setting, music_folder, game, music_from = (None,)):
        self.circle_game = True
        self.root = root
        self.ad_video = setting.game_idle_video
        if music_from is None:
            music_from_local = setting.local_music
        else:
            music_from_local = music_from
        if music_from_local:
            self.rule_introduce = setting.game_name
            self.bmg_video = setting.game_bg_audio
            self.count_down = setting.game_start_video
            self.red_tread = setting.game_blood
            self.clap_light = None
            self.error_clap = None
            self.correct = None
            self.blue_tread = setting.game_scode
            self.game_accomplished = setting.game_pass
        else:
            self.rule_introduce = self.get_video_path(music_folder, game.rule_introduce)
            self.bmg_video = self.get_video_path(music_folder, game.bmg_video)
            self.count_down = self.get_video_path(music_folder, game.count_down)
            self.red_tread = self.get_video_path(music_folder, game.red_tread)
            self.clap_light = self.get_video_path(music_folder, game.clap_light)
            self.error_clap = self.get_video_path(music_folder, game.error_clap)
            self.correct = self.get_video_path(music_folder, game.correct)
            self.blue_tread = self.get_video_path(music_folder, game.blue_tread)
            self.game_accomplished = self.get_video_path(music_folder, game.game_accomplished)


