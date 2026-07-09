# Source Generated with Decompyle++
# File: game_hw.pyc (Python 3.7)

import time
import traceback
from tkinter import messagebox
from loguru import logger
from gui.language import language
from led import led_control
from led.led_control_c import LedControl
from model.setting import Setting

class GameHW:
    
    def init_hw_led(self, setting):
        if Setting.USE_SERIAL_HD:
            logger.debug('init_hw_led')
            self.led_col_wall_light = LedControl()
            serial_list_error = self.led_col_wall_light.init_com(setting.list_wall_com_info)
            for serial in serial_list_error:
                messagebox.showerror(language.SERIAL_OPEN_FAIL, serial)
                return False
            
            self.led_col_wall_screen = LedControl()
            serial_list_error = self.led_col_wall_screen.init_com(setting.list_screen_com_info)
            for serial in serial_list_error:
                messagebox.showerror(language.SERIAL_OPEN_FAIL, serial)
                return False
            
            serial_list_error = led_control.init_com(setting.list_com_info)
            led_row = int(setting.value_high)
            led_col = int(setting.value_width)
            led_control.init_layout(setting.type, led_row, led_col, setting.floor_layout_coors_no_use)
            for serial in serial_list_error:
                messagebox.showerror(language.SERIAL_OPEN_FAIL, serial)
                return False
            
            return True
        return None

    
    def update_hw_led(self):
        if Setting.USE_SERIAL_HD:
            led_control.update_led(self.setting.type, self.led_table.led_table, self.led_table.get_state_table(), self.led_table.get_state_2array(), self.led_table.get_g_wall_has_been_tread_arr2())
            self.led_col_wall_light.update_wall_light(self.led_table.get_wall_light_arr(), self.led_table.get_wall_light_state_array(), self.setting.wall_light_layout_real, self.setting.wall_light_layout_logic)
            self.led_col_wall_screen.update_wall_screen(self.led_table.get_wall_screen_arr(), self.setting.wall_light_layout_real)

    
    def draw_hw_led_color(self):
        if Setting.USE_SERIAL_HD:
            
            try:
                ret = led_control.draw_led_color(self.setting.type, self.led_table.led_table)
                logger.debug('serial wall light draw')
                if self.setting.light:
                    self.led_col_wall_light.draw_wall_light_color(self.led_table.get_wall_light_arr(), self.setting.wall_light_layout_real)
                logger.debug('end')
                logger.debug('serial wall screen draw')
                if self.setting.screen:
                    self.led_col_wall_screen.update_wall_screen(self.led_table.get_wall_screen_arr(), self.setting.wall_light_layout_real)
                logger.debug('end')
            except:
                logger.error('draw_hw_led_color {}', traceback.format_exc())


    
    def __init__(self, setting, led_table):
        self.led_col_wall_screen = None
        self.led_col_wall_light = None
        self.hardware_is_open = self.init_hw_led(setting)
        self.setting = setting
        self.led_table = led_table

    
    def hw_led_close(self):
        logger.info('idle game hw_led_close')
        if Setting.USE_SERIAL_HD:
            led_control.close_com()
            if self.led_col_wall_screen is not None:
                self.led_col_wall_screen.close_com()
            if self.led_col_wall_light is not None:
                self.led_col_wall_light.close_com()

    
    def reopen_com(self):
        self.hw_led_close()
        self.init_hw_led(self.setting)
        logger.info('idle game reopen_com')


