# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: idle_video_play.py
import os, subprocess, sys, time, traceback, loguru, pygame
from moviepy.editor import VideoFileClip
import threading

class IdleVideoPlay(threading.Thread):

    def __init__(self, parent, video_path, size=(1080, 1920), wait_time=5):
        threading.Thread.__init__(self)
        loguru.logger.debug(self.__str__())
        self.video_path = video_path
        self.idle_video = None
        self.video_size = size
        self.is_looping = True
        self.video_is_opened = False
        self.last_time = time.time()
        self.wait_time = wait_time
        self.parent = parent
        self.thread_is_ending = False

    def close_video(self):
        if self.idle_video:
            self.idle_video.terminate()
            self.idle_video.wait()
            self.idle_video = None
        loguru.logger.info("end close idle video")

    def reset(self):
        self.last_time = time.time()
        if self.idle_video:
            self.video_is_opened = False
            self.close_video()
            self.parent.open_video_introduce()
            loguru.logger.debug("video is close")

    def stop_running(self):
        loguru.logger.info("start stop idle video")
        self.is_looping = False
        while not self.thread_is_ending:
            self.parent.root.update()
            time.sleep(0.01)

        self.close_video()

    def run(self):
        loguru.logger.info("IdleVideo run th")
        try:
            rlt_path = os.path.relpath(self.video_path)
            vlc_command = [
             './use_dll/exe/vlc', 
             '--no-stats', 
             '--no-video-title-show', 
             '--loop', 
             rlt_path]
            while self.is_looping:
                time.sleep(0.1)
                cur_time = time.time()
                time_pass = cur_time - self.last_time
                if time_pass > self.wait_time and self.idle_video is None and self.is_looping:
                    self.parent.close_video_introduce()
                    self.idle_video = subprocess.Popen(vlc_command)
                    self.video_is_opened = True
                    loguru.logger.debug(self.__str__() + self.idle_video.__str__())

            self.thread_is_ending = True
        except:
            self.thread_is_ending = True
            loguru.logger.error(traceback.format_exc())

    def run_old(self):
        clip = self.idle_video
        while self.is_looping:
            cur_time = time.time()
            time_pass = cur_time - self.last_time
            if time_pass > self.time_pass:
                print("new clip")
                clip = VideoFileClip((self.video_path), target_resolution=(self.video_size))
                self.video_is_opened = True
                self.idle_video = clip
                while self.video_is_opened:
                    try:
                        clip.preview()
                    except:
                        try:
                            pygame.display.quit()
                        except:
                            print("except pygame.display.quit()")

                        print("except clip preview")

        if clip is not None:
            clip.close()
            pygame.display.quit()

# okay decompiling /games/climb/climb_source_code/util/idle_video_play.pyc
