# Source Generated with Decompyle++
# File: audio.pyc (Python 3.7)

from pygame import mixer

class Audio:
    
    def get_init(self):
        init = mixer.get_init()
        return init

    
    def init(self):
        print('audio init')
        mixer.quit()
        mixer.init(4096, **('buffer',))

    
    def play_sync(self, audio_name):
        mixer.music.load(audio_name)
        mixer.music.play()

    
    def play(self, audio_name):
        
        try:
            mixer.find_channel(True, **('force',)).play(mixer.Sound(audio_name))
        except:
            pass


    
    def stop(self):
        print('audio stop')
        mixer.stop()
        mixer.music.unload()

    
    def quit(self):
        mixer.quit()

    
    def queue(self, filename):
        
        try:
            if self.get_busy():
                mixer.music.queue(filename)
            else:
                self.play_bmg(filename)
        except:
            pass


    
    def get_busy(self):
        return mixer.music.get_busy()

    
    def play_bmg(self, audio_file_name, start_second, loops = (0, 0)):
        ret = True
        time_tmp = 0
        
        try:
            mixer.music.load(audio_file_name)
            mixer.music.play(loops, start_second, **('loops', 'start'))
        except:
            ret = False

        return ret


