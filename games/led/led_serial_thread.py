# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: led_serial_thread.py
import threading, time
from tkinter import messagebox
import gui.language as language
from led import communication

class LedSerialThread(threading.Thread):

    def __init__(self, root, com_name, led_start_var, led_end_var, text_var):
        threading.Thread.__init__(self)
        self.text_var = text_var
        com_obj = communication.Communication(com_name, 115200, 0.5)
        self.com_obj = com_obj
        self.led_start_var = led_start_var
        self.led_end_var = led_end_var
        self.text_var = text_var
        self.root = root
        self.com_name = com_name

    def stop(self):
        if self.com_obj:
            if self.com_obj.main_engine:
                self.com_obj.main_engine.close()

    def run(self):
        self.array_com_protocal_black = []
        self.array_com_protocal = []
        read_size = 1000
        last_time = time.time()
        switch_color = True
        com_obj = self.com_obj
        led_start_var = self.led_start_var
        led_end_var = self.led_end_var
        text_var = self.text_var
        if com_obj.main_engine is not None and com_obj.main_engine.is_open:
            while self.text_var.get() == language.STOP:
                try:
                    read_buffer = com_obj.main_engine.read(read_size)
                    index1_of_fc = read_buffer.index(252)
                    index2_of_fc = read_buffer[(index1_of_fc + 1)[:None]].index(252)
                    led_nums = index2_of_fc - 1
                    led_end_var.set(led_nums + int(led_start_var.get()) - 1)
                    if led_nums > 0:
                        array_com_protocal = [
                         255, 255]
                        self.array_com_protocal = array_com_protocal
                        for i in range(led_nums):
                            array_com_protocal.append(171)
                            array_com_protocal.append(171)
                            array_com_protocal.append(171)

                        array_com_protocal[2] = 0
                        array_com_protocal[3] = 0
                        array_com_protocal[4] = 254
                        array_com_protocal[-3] = 254
                        array_com_protocal[-2] = 0
                        array_com_protocal[-1] = 0
                        array_com_protocal_black = [
                         255, 255]
                        self.array_com_protocal_black = array_com_protocal_black
                        for i in range(led_nums):
                            for j in range(3):
                                array_com_protocal_black.append(0)

                except:
                    pass

                time.sleep(0.2)
                current_time = time.time()
                time_pass = current_time - last_time
                if time_pass > 1:
                    switch_color = not switch_color
                    last_time = current_time
                    if switch_color:
                        self.com_obj.Send_data(self.array_com_protocal_black)
                    else:
                        self.com_obj.Send_data(self.array_com_protocal)

            self.com_obj.Send_data(self.array_com_protocal_black)
            self.com_obj.main_engine.close()
            self.com_obj = None
        else:
            text_var.set(language.TEST)
            messagebox.showerror((language.SERIAL), (self.com_name + language.SERIAL_OPEN_FAIL), parent=(self.root))


class ScreenSerialThread(threading.Thread):

    def __init__(self, root, com_name, led_start_var, led_end_var, text_var):
        threading.Thread.__init__(self)
        self.com_name = com_name
        self.led_start_var = led_start_var
        self.led_end_var = led_end_var
        self.text_var = text_var
        self.root = root

    def run(self):
        com_name = self.com_name
        led_start_var = self.led_start_var
        led_end_var = self.led_end_var
        text_var = self.text_var
        com_obj = communication.Communication(com_name, 115200, 0.5)
        last_time = time.time()
        if com_obj.main_engine is not None and com_obj.main_engine.is_open:
            try:
                led_nums = int(led_end_var.get()) - int(led_start_var.get()) + 1
                if led_nums <= 0:
                    led_nums = 1
                if led_nums > 0:
                    array_com_protocal = [
                     255, 1, 1, 1, 3, 
                     85]
                    address_idx = 1
                    num_text_idx = 2
                    verify_code_idx = 4
                    color_idx = 3
                    switch_color = False
                    while text_var.get() == language.STOP:
                        time.sleep(0.1)
                        current_time = time.time()
                        time_pass = current_time - last_time
                        index = round(time_pass / 0.5) % 3
                        if index == 0:
                            array_com_protocal[color_idx] = 2
                        else:
                            if index == 1:
                                array_com_protocal[color_idx] = 3
                            else:
                                array_com_protocal[color_idx] = 4
                        for i in range(led_nums):
                            array_com_protocal[address_idx] = i + 1
                            array_com_protocal[num_text_idx] = i + 1
                            array_com_protocal[verify_code_idx] = 2 * i + 2 + array_com_protocal[color_idx]
                            com_obj.Send_data(array_com_protocal)

                    com_obj.main_engine.close()
            except:
                if com_obj is not None and com_obj.main_engine is not None:
                    if com_obj.main_engine.is_open:
                        text_var.set(language.TEST)
                        com_obj.main_engine.close()

        else:
            text_var.set(language.TEST)
            messagebox.showerror((language.SERIAL), (com_name + language.SERIAL_OPEN_FAIL), parent=(self.self.root))

# okay decompiling /games/climb/climb_source_code/led/led_serial_thread.pyc
