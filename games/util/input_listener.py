# Source Generated with Decompyle++
# File: input_listener.pyc (Python 3.7)

from pynput import keyboard, mouse

class InputListener:
    
    def __init__(self, partial = (None,)):
        mouse_listener = mouse.Listener(self.on_click, self.on_scroll, **('on_click', 'on_scroll'))
        self.mouse_listener = mouse_listener
        mouse_listener.start()
        keyboard_listener = keyboard.Listener(self.on_press, **('on_press',))
        self.keyboard_listener = keyboard_listener
        keyboard_listener.start()
        self.partial = partial

    
    def stop(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()

    
    def on_move(self, x, y):
        pass

    
    def on_click(self, x, y, button, pressed):
        self.partial()

    
    def on_scroll(self, x, y, dx, dy):
        self.partial()

    
    def on_press(self, key):
        self.partial()


