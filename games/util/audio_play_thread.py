# Source Generated with Decompyle++
# File: audio_play_thread.pyc (Python 3.7)

import sys
import threading
import time
import traceback
import loguru
import numpy as np
import pygame
from audio_play import audio

class AudioPlayThread(threading.Thread):
    
    def __init__(self, clip_audio, buffersize, nbytes = (4096, 2)):
        threading.Thread.__init__(self)
        audio_init = audio.Audio().get_init()
        self.running_state = True
        self.clip_audio = clip_audio
        self.fps = audio_init[0]
        self.buffersize = buffersize
        self.nbytes = nbytes

    
    def run(self):
        fps = self.fps
        clip = self.clip_audio
        self.running_end = False
        if clip:
            loguru.logger.info('AudioPlayThread running')
            
            try:
                buffersize = self.buffersize
                nbytes = self.nbytes
                totalsize = int(fps * clip.duration)
                pospos = np.array(list(range(0, totalsize, buffersize)) + [
                    totalsize])
                tt = (1 / fps) * np.arange(pospos[0], pospos[1])
                sndarray = clip.to_soundarray(tt, nbytes, True, **('nbytes', 'quantize'))
                chunk = pygame.sndarray.make_sound(sndarray)
                channel = chunk.play()
                lenght = 0
                for i in range(1, len(pospos) - 1):
                    if self.running_state:
                        tt = (1 / fps) * np.arange(pospos[i], pospos[i + 1])
                        sndarray = clip.to_soundarray(tt, nbytes, True, **('nbytes', 'quantize'))
                        chunk = pygame.sndarray.make_sound(sndarray)
                        lenght = chunk.get_length()
                        chunk.play()
                        if lenght > 4:
                            break
                        time.sleep(lenght)
                        continue
            except:
                loguru.logger.error('audio thread running except {}', traceback.format_exc())

            self.running_end = True
            loguru.logger.info('audio thread running end. {}', lenght)


