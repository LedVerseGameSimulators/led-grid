# Source Generated with Decompyle++
# File: gm_introduce_video_new.pyc (Python 3.7)

import os
import shelve
import sys
import threading
import time
import traceback
from tkinter import Tk, Label, NW, YES, BOTH, Canvas
import cv2
import loguru
import numpy as np
import pygame
from PIL import ImageTk, Image
from moviepy.editor import VideoFileClip
from moviepy.video.fx.resize import resize
from util.audio_play_thread import AudioPlayThread

class TkVideoPlayNew(threading.Thread):
    
    def __init__(self, video_path, movie_label, loop, video_size = (-1, None)):
        threading.Thread.__init__(self)
        self.circle = False
        self.running_ending = True
        self.video = None
        self.audio_thread = None
        self.loop = loop
        if not video_path is None and video_path == '':
            self.video = None
            self.imgtk = None
            self.last_time = 0
            self.circle = True
            self.running_ending = False
            
            try:
                if video_size:
                    self.video = VideoFileClip(video_path, (int(video_size[1] / 2), int(video_size[0] / 2)), **('target_resolution',))
                    self.video = self.video.resize(video_size)
                else:
                    self.video = VideoFileClip(video_path)
            except:
                pass

            ff_opts = {
                'loop': 0,
                'an': False }
            self.movieLabel = movie_label
            if video_size:
                self.video_size = video_size
            else:
                self.video_size = (self.movieLabel.winfo_width(), self.movieLabel.winfo_height())
            self.video_path = video_path

    
    def waiting(self):
        i = 0
        while self.audio_thread.running_end and i < 150:
            if self.movieLabel:
                self.movieLabel.update()
            time.sleep(0.02)
            i += 1
        if i > 150:
            raise Exception('waiting audio running end time out ')

    
    def run(self):
        loguru.logger.info('TkVideoPlayNew running ')
        photo = None
        if self.video:
            while self.circle and self.loop:
                fps = self.video.fps
                video_duration = self.video.duration - 0.1
                if self.video.audio:
                    audio_thread = AudioPlayThread(self.video.audio)
                    self.audio_thread = audio_thread
                    audio_thread.start()
                
                try:
                    time_pass = 0
                    time_start = time.time()
                    frm_num = 0
                    while time_pass < video_duration:
                        if self.video:
                            now = time.time()
                            time_pass = now - time_start
                            theory_time = (1 / fps) * frm_num
                            time_gap = theory_time - time_pass
                            if time_gap > 0:
                                time.sleep(time_gap)
                                time_pass = theory_time
                            frm_num += 1
                            image = self.video.get_frame(time_pass)
                            current_image = Image.fromarray(image)
                            photo = ImageTk.PhotoImage(current_image, **('image',))
                            self.movieLabel.config(photo, **('image',))
                            self.movieLabel.image = photo
                            continue
                        break
                    loguru.logger.info('start to close audio running')
                    if self.audio_thread:
                        audio_thread.running_state = False
                        self.waiting()
                    loguru.logger.info('one loop of video end')
                except:
                    loguru.logger.error('start to close audio running')
                    if self.audio_thread:
                        audio_thread.running_state = False
                        loguru.logger.error('video running except {}', traceback.format_exc())
                        
                        try:
                            self.waiting()
                        except:
                            loguru.logger.error('video running except {}', traceback.format_exc())


                self.loop -= 1
        self.running_ending = True
        loguru.logger.info('TkVideoPlayNew running end')

    
    def run_old2(self):
        video = self.video
        lbVideo = self.movieLabel
        for frame in video.iter_frames(video.fps, **('fps',)):
            current_image = Image.fromarray(frame).resize((lbVideo.winfo_width(), lbVideo.winfo_height()))
            frame = ImageTk.PhotoImage(current_image)
            lbVideo['image'] = frame
            lbVideo.image = frame
            lbVideo.update()
        

    
    def update_frame(self):
        video = self.video
        video_path = self.video_path
        movieLabel = self.movieLabel
        if video.isOpened():
            (ret, frame) = video.read()
            if frame is None:
                print('frame read failure')
            if ret:
                
                try:
                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    current_image = Image.fromarray(img).resize((movieLabel.winfo_width(), movieLabel.winfo_height()))
                    photo = ImageTk.PhotoImage(current_image, **('image',))
                    self.movieLabel.config(photo, **('image',))
                    self.movieLabel.image = photo
                except:
                    pass

                movieLabel.update()
            else:
                print('video read failure')
                video.release()
                cv2.destroyAllWindows()
                self.video = cv2.VideoCapture(video_path)
        else:
            print('video not open')

    
    def audio_play(self, clip, audioFlag, videoFlag, stopFlag, fps, buffersize, nbytes = (None, None, False, 22050, 3000, 2)):
        pygame.mixer.quit()
        pygame.mixer.init(fps, -16, 2, 1024, **('frequency', 'size', 'channels', 'buffer'))
        totalsize = int(fps * clip.duration)
        pospos = np.array(list(range(0, totalsize, buffersize)) + [
            totalsize])
        tt = (1 / fps) * np.arange(pospos[0], pospos[1])
        sndarray = clip.to_soundarray(tt, nbytes, True, **('nbytes', 'quantize'))
        chunk = pygame.sndarray.make_sound(sndarray)
        channel = chunk.play()
        for i in range(1, len(pospos) - 1):
            if stopFlag:
                tt = (1 / fps) * np.arange(pospos[i], pospos[i + 1])
                sndarray = clip.to_soundarray(tt, nbytes, True, **('nbytes', 'quantize'))
                chunk = pygame.sndarray.make_sound(sndarray)
                while channel.get_queue():
                    time.sleep(0.003)
                channel.queue(chunk)
                continue
        

    
    def set_video(self, video_path):
        print('set_video', video_path)
        if self.video:
            video = self.video
            self.video = None
            video.close()
        if not video_path is None and video_path == '':
            ff_opts = {
                'loop': 0 }
            
            try:
                self.video = VideoFileClip(video_path)
                self.video = self.video.resize(self.video_size)
                self.video_path = video_path
            except:
                pass


    
    def close_video(self, root):
        loguru.logger.info('start to close video')
        self.circle = False
        if self.video:
            video = self.video
            self.video = None
            if self.audio_thread:
                self.audio_thread.running_state = False
                
                try:
                    self.waiting()
                except:
                    loguru.logger.error('close audio except {}', traceback.format_exc())

            video.close()
        i = 0
        while self.running_ending and i < 150:
            if root:
                root.update()
            time.sleep(0.02)
            i += 1
        if i > 150:
            loguru.logger.info('close video except time out')
        loguru.logger.info('close video end')


