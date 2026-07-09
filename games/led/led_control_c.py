# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: led_control_c.py
import shelve, sys
import encryption.yanqian as yanqian
from led import communication, position_convert
from loguru import logger
import traceback
from model.setting import Setting
from util import util_program
import gui.language as language

class LedControl:

    def get_com_num(self, com_info_str):
        try:
            idx_com_name_start = com_info_str.index("(")
            idx_com_name_end = com_info_str.index(")")
            com_name = com_info_str[idx_com_name_start + 1:idx_com_name_end]
            return com_name
        except:
            logger.debug("get_com_num exception")
            return com_info_str

    def init_com(self, list_com_info):
        global com_is_block
        list_com = []
        self.list_com = list_com
        list_serial_open_error = []
        self.last_com_send_data = None
        self.com_send_arr = None
        if not list_com_info is None:
            if len(list_com_info) == 0:
                return list_serial_open_error
            if yanqian():
                f = shelve.open("./setting/debug_parameter")
                com_is_block = f.get("com_is_block")
                f.close()
                logger.warning("串口阻塞{}", com_is_block)
                i = 0
                for com_info in list_com_info:
                    com_name = self.get_com_num(com_info[0])
                    obj_com = communication.Communication(com_name, 115200, 0.3)
                    if obj_com.main_engine is None:
                        list_serial_open_error.append(com_name)
                        continue
                    list_com.append([obj_com, com_info[1], com_info[2]])

        else:
            list_serial_open_error = [
             language.UN_AUTHOR]
        return list_serial_open_error

    def init_led_screen(self, list_com_info, screen_height, screen_width, layout_type):
        global m_col
        global m_layout_type
        global m_led_color_one_array
        global m_led_state_one_array
        global m_led_state_two_array
        global m_row
        self.init_com(list_com_info)
        m_layout_type = layout_type
        m_led_state_one_array = [
         False] * screen_height * screen_width
        m_led_state_two_array = [[False] * screen_width for _ in range(screen_height)]
        m_led_color_one_array = [] * screen_height * screen_width
        m_row = screen_height
        m_col = screen_width

    def get_com_name_list(self):
        list_com_name = []
        list_com_info = communication.Communication.get_com_list()
        for com in list_com_info:
            list_com_name.append(com.name)

        return list_com_name

    def close_com(self):
        logger.info("close com wall light or screen")
        list_com = self.list_com
        if list_com is not None:
            for com in list_com:
                com[0].Close_Engine()

    def draw_wall_screen_by_com(self, address, num_text, color=1):
        list_com = self.list_com
        if Setting.USE_SERIAL_HD:
            i = 0
            try:
                for com in list_com:
                    array_com_protocal = [
                     255]
                    array_com_protocal.append(address)
                    array_com_protocal.append(num_text)
                    array_com_protocal.append(color)
                    n = address + num_text + color
                    array_com_protocal.append(n)
                    array_com_protocal.append(85)
                    com[0].Send_data(array_com_protocal)
                    i += 1

            except:
                logger.error("send wall screen text data {}", traceback.format_exc())
                logger.error(list_com[i][0].port)

    def draw_screen_by_com(self, layout_type, logic_2array):
        list_com = self.list_com
        if Setting.USE_SERIAL_HD:
            row = len(logic_2array)
            col = len(logic_2array[0])
            one_array = [
             ()] * row * col
            position_convert.position_convert_2arr_to_1arr(layout_type, logic_2array, one_array)
            try:
                for com in list_com:
                    values = [
                     com[1], com[2]]
                    array = one_array[int(values[0]) - 1:int(values[1])]
                    array_com_protocal = [255, 255]
                    for tuple in list(reversed(array)):
                        array_com_protocal.append(tuple[0])
                        array_com_protocal.append(tuple[1])
                        array_com_protocal.append(tuple[2])

                    com[0].Send_data(array_com_protocal)

            except:
                pass

    def draw_wall_light_by_com(self, data_array):
        list_com = self.list_com
        i = 0
        try:
            for com in list_com:
                values = [
                 com[1], com[2]]
                array_com_protocal = [
                 255, 255]
                for tuple in list(reversed(data_array)):
                    array_com_protocal.append(tuple[0])
                    array_com_protocal.append(tuple[1])
                    array_com_protocal.append(tuple[2])

                com[0].Send_data(array_com_protocal)
                i += 1

        except:
            logger.error("send wall button light color data {}", traceback.format_exc())
            logger.error(list_com[i][0].port)

    def display_led_screen(self):
        list_com = self.list_com
        try:
            for com in list_com:
                values = [
                 com[1], com[2]]
                array = m_led_color_one_array[int(values[0]) - 1:int(values[1])]
                array_com_protocal = [255, 255]
                for tuple in list(reversed(array)):
                    array_com_protocal.append(tuple[0])
                    array_com_protocal.append(tuple[1])
                    array_com_protocal.append(tuple[2])

                com[0].Send_data(array_com_protocal)

        except:
            pass

    def index_form_last(self, buffer, char, size_data):
        size = len(buffer)
        if size >= size_data * 2:
            start_search = size - size_data
            for i in range(start_search, -1, -1):
                if buffer[i] == char:
                    return i

        else:
            for i in range(size):
                if buffer[i] == char:
                    return i

    def read(self, com, rst_arr, start_num, read_size=3, block=False):
        in_len = com.in_waiting
        if in_len >= read_size + 2:
            data_read_buffer = com.read_all()
        else:
            if block:
                data_read_buffer = com.read(read_size + 2)
            else:
                data_read_buffer = com.read_all()
        in_len = len(data_read_buffer)
        if not in_len % (read_size + 2) != 0:
            if in_len == 0:
                logger.debug("{} read size {}", com.name, in_len)
            if in_len > 2:
                if in_len >= read_size + 2:
                    data_want = data_read_buffer[in_len - (read_size + 2):]
        else:
            data_want = data_read_buffer
        index_of_fc = data_want.index(252)
        start_fc_idx = index_of_fc + 2
        arr_after_fc = data_want[start_fc_idx:]
        len_arr_after_fc = len(arr_after_fc)
        last_num = start_num + read_size - 1
        for i in range(len_arr_after_fc):
            rst_arr[last_num - i] = arr_after_fc[i] == 10

        if index_of_fc > 0:
            arr_before_fc = data_want[:index_of_fc]
            len_arr_before_fc = len(arr_before_fc)
            for i in range(len_arr_before_fc):
                rst_arr[i + start_num] = arr_before_fc[len_arr_before_fc - i - 1] == 10

    def update_screen_state_by_com_old(self, layout_type, state_table, state_2array):
        list_com = self.list_com
        col = len(state_2array[0])
        row = len(state_2array)
        one_array = [False] * row * col
        position_convert.position_convert_2arr_to_1arr(layout_type, state_table, one_array)
        data_rst = []
        has_read_state = True
        for com in list_com:
            try:
                values = [com[1], com[2]]
                src_idx_start = int(values[0]) - 1
                src_idx_end = int(values[1])
                size = src_idx_end - src_idx_start
                size = (size + 1 + 1) * 2 - 1
                data_read_buffer = com[0].main_engine.read_all()
                index_of_fc = data_read_buffer.index(252)
                start = index_of_fc + 2
                end = index_of_fc + 2 + data_read_buffer[index_of_fc + 1]
                data_rst = data_read_buffer[start:end]
                tmp = src_idx_end - 1
                for i in range(src_idx_start, src_idx_end):
                    one_array[i] = data_rst[tmp - i] == 10

            except:
                pass

        position_convert.position_convert_1arr_to_2arr(layout_type, one_array, state_2array)

    def update_screen_state_by_com(self, layout_type, state_table, state_2array):
        list_com = self.list_com
        col = len(state_2array[0])
        row = len(state_2array)
        one_array = [False] * row * col
        position_convert.position_convert_2arr_to_1arr(layout_type, state_table, one_array)
        logger.debug("read state")
        for com in list_com:
            try:
                values = [com[1], com[2]]
                src_idx_start = int(values[0]) - 1
                src_idx_end = int(values[1])
                size = src_idx_end - src_idx_start
                self.read((com[0].main_engine), one_array, src_idx_start, read_size=size, block=com_is_block)
            except:
                logger.error("{} except: {} ", com[0].main_engine.name, traceback.format_exc())

        position_convert.position_convert_1arr_to_2arr(layout_type, one_array, state_2array)

    def update_wall_light_state_by_com(self, state_array):
        list_com = self.list_com
        for com in list_com:
            try:
                src_idx_start = 0
                size = len(state_array)
                self.read((com[0].main_engine), state_array, src_idx_start, read_size=size, block=com_is_block)
                logger.debug("read wall light state{}", size)
            except:
                logger.error("{} except: {} ", com[0].main_engine.name, traceback.format_exc())

    def clear_com_buffer(self):
        list_com = self.list_com
        if com_is_block:
            for com in list_com:
                com[0].main_engine.flushInput()

    def update_screen_state_by_com_new(self, layout_type, state_table):
        list_com = self.list_com
        col = len(state_table[0])
        row = len(state_table)
        one_array = [False] * row * col
        position_convert.position_convert_2arr_to_1arr(layout_type, state_table, one_array)
        logger.debug("read state")
        for com in list_com:
            try:
                values = [com[1], com[2]]
                src_idx_start = int(values[0]) - 1
                src_idx_end = int(values[1])
                size = src_idx_end - src_idx_start
                self.read((com[0].main_engine), one_array, src_idx_start, read_size=size, block=com_is_block)
            except:
                logger.error("{} except: {} ", com[0].main_engine.name, traceback.format_exc())

        position_convert.position_convert_1arr_to_2arr(layout_type, one_array, state_table)

    def get_led_screen_state(self):
        data_rst = []
        has_read_state = True
        list_com = self.list_com
        for com in list_com:
            try:
                values = [
                 com[1], com[2]]
                src_idx_start = int(values[0]) - 1
                src_idx_end = int(values[1])
                size = src_idx_end - src_idx_start
                size = (size + 1 + 1) * 2 - 1
                data_read_buffer = com[0].main_engine.read_all()
                index_of_fc = data_read_buffer.index(252)
                start = index_of_fc + 2
                end = index_of_fc + 2 + data_read_buffer[index_of_fc + 1]
                data_rst = data_read_buffer[start:end]
                tmp = src_idx_end - 1
                for i in range(src_idx_start, src_idx_end):
                    m_led_state_one_array[i] = data_rst[tmp - i] == 10

            except:
                pass

        position_convert.position_convert_1arr_to_2arr(m_layout_type, m_led_state_one_array, m_led_state_two_array)

    def real_led_to_screen_virtual_led_state_switch(self, table_real_led, table_virtual_led, g_wall_has_been_tread_arr2=None):
        if g_wall_has_been_tread_arr2 is not None:
            for i in range(len(table_real_led)):
                for j in range(len(table_real_led[i])):
                    if not table_virtual_led[i][j]:
                        if table_real_led[i][j]:
                            g_wall_has_been_tread_arr2[i][j] = True
                    table_virtual_led[i][j] = table_real_led[i][j]

        else:
            for i in range(len(table_real_led)):
                for j in range(len(table_real_led[i])):
                    table_virtual_led[i][j] = table_real_led[i][j]

    def update_led(self, setting, logic_2array, table_state, state_2array, g_wall_has_been_tread_arr2):
        list_com = self.list_com
        if len(list_com) > 0:
            self.draw_screen_by_com(setting, logic_2array)
            self.update_screen_state_by_com(setting, table_state, state_2array)
            self.real_led_to_screen_virtual_led_state_switch(state_2array, table_state, g_wall_has_been_tread_arr2)

    def update_wall_light(self, array_logic, array_state, array_index, array_index_logic):
        list_com = self.list_com
        if len(list_com) > 0:
            arr_read = [
             0] * len(array_index)
            arr_send = []
            for i in array_index:
                arr_send.append(array_logic[i - 1])

            logger.debug("wall led color update")
            self.draw_wall_light_by_com(arr_send)
            logger.debug("end")
            logger.debug("wall led state update")
            self.update_wall_light_state_by_com(arr_read)
            logger.debug("end")
            j = 0
            for i in array_index:
                array_state[i - 1] = arr_read[j]
                j += 1

    def draw_wall_light_color(self, array_logic, array_index):
        list_com = self.list_com
        if len(list_com) > 0:
            arr_send = []
            for i in array_index:
                arr_send.append(array_logic[i - 1])

            logger.debug("wall led color update")
            self.draw_wall_light_by_com(arr_send)
            logger.debug("end")

    def get_wall_light_state(self, array_state, array_index):
        list_com = self.list_com
        if len(list_com) > 0:
            arr_read = [
             0] * len(array_index)
            logger.debug("wall led state update")
            self.update_wall_light_state_by_com(arr_read)
            logger.debug("end")
            j = 0
            for i in array_index:
                array_state[i - 1] = arr_read[j]
                j += 1

    def update_wall_screen(self, array_logic, array_index):
        list_com = self.list_com
        if len(list_com) > 0:
            text_num_send = 0
            address = 1
            for i in array_index:
                text_num_send = array_logic[i - 1]
                self.draw_wall_screen_by_com(address, text_num_send)
                address += 1

    def update_wall_screen_new(self, array_wall_light):
        send_arr = position_convert.wall_light_logic2real(array_wall_light, self.wall_start, self.direct)
        for obj in self.list_delete:
            send_arr.remove(obj)

        list_com = self.list_com
        if self.last_com_send_data is None:
            self.last_com_send_data = []
            for i in range(len(send_arr)):
                self.last_com_send_data.append(-1)

        if len(list_com) > 0:
            text_num_send = 0
            address = 1
            i = 0
            for data in send_arr:
                if data != self.last_com_send_data[i]:
                    self.draw_wall_screen_by_com(address, text_num_send)
                address += 1

        self.last_com_send_data = send_arr

# okay decompiling /games/climb/climb_source_code/led/led_control_c.pyc
