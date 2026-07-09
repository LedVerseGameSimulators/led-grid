# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52)
# [GCC 12.2]
# Embedded file name: led_control.py
import os
import shelve, sys
import encryption.yanqian as yanqian

_GAMES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEBUG_PARAM = os.path.join(_GAMES_DIR, 'setting', 'debug_parameter')
from led import communication, position_convert
from loguru import logger
import traceback
from model.setting import Setting
from util import util_program
list_com = []
m_led_state_one_array = None
m_led_state_two_array = None
m_led_color_one_array = None
m_layout_type = None
m_row = 0
m_col = 0
com_is_block = False
g_has_open = False
rect_position_arr = None

def init_layout(layout_type, layout_row, layout_col, position_no_use):
    global rect_position_arr
    rect_position_arr = [
     None] * layout_row * layout_col
    position_convert.record_rect_position_in_order_by_layout(layout_type, layout_row, layout_col, rect_position_arr)
    for coors in rect_position_arr.copy():
        if coors in position_no_use:
            rect_position_arr.remove(coors)


def get_com_num(com_info_str):
    try:
        idx_com_name_start = com_info_str.index("(")
        idx_com_name_end = com_info_str.index(")")
        com_name = com_info_str[idx_com_name_start + 1:idx_com_name_end]
        return com_name
    except:
        logger.debug("get_com_num exception")
        return com_info_str


def init_com(list_com_info):
    global com_is_block
    global g_has_open
    global list_com
    list_com = []
    list_serial_open_error = []
    logger.info("init_com floor")
    if yanqian.yanqian():
        f = shelve.open(_DEBUG_PARAM)
        com_is_block = f.get("com_is_block")
        f.close()
        logger.warning("串口阻塞{}", com_is_block)
        i = 0
        for com_info in list_com_info:
            com_name = get_com_num(com_info[0])
            obj_com = communication.Communication(com_name, 115200, 0.3)
            if obj_com.main_engine is None:
                list_serial_open_error.append(com_name)
                continue
            list_com.append([obj_com, com_info[1], com_info[2]])

        if len(list_com) > 0:
            g_has_open = True
    return list_serial_open_error


def init_led_screen(list_com_info, screen_height, screen_width, layout_type):
    global m_col
    global m_layout_type
    global m_led_color_one_array
    global m_led_state_one_array
    global m_led_state_two_array
    global m_row
    init_com(list_com_info)
    m_layout_type = layout_type
    m_led_state_one_array = [
     False] * screen_height * screen_width
    m_led_state_two_array = [[False] * screen_width for _ in range(screen_height)]
    m_led_color_one_array = [] * screen_height * screen_width
    m_row = screen_height
    m_col = screen_width


def get_com_name_list():
    list_com_name = []
    list_com_info = communication.Communication.get_com_list()
    for com in list_com_info:
        list_com_name.append(com.description)

    return list_com_name


def close_com():
    global g_has_open
    logger.info("close_com floor")
    if list_com is not None:
        for com in list_com:
            com[0].Close_Engine()

    g_has_open = False


def draw_screen_by_com(layout_type, logic_2array):
    if Setting.USE_SERIAL_HD:
        row = len(logic_2array)
        col = len(logic_2array[0])
        i = 0
        try:
            for com in list_com:
                values = [
                 com[1], com[2]]
                array = rect_position_arr[int(values[0]) - 1:int(values[1])]
                array_com_protocal = [255, 255]
                for coors in list(reversed(array)):
                    ri, ci = coors[0], coors[1]
                    if 0 <= ri < row and 0 <= ci < col:
                        tuple_color = logic_2array[ri][ci]
                    else:
                        tuple_color = (0, 0, 0)
                    array_com_protocal.append(tuple_color[0])
                    array_com_protocal.append(tuple_color[1])
                    array_com_protocal.append(tuple_color[2])

                com[0].Send_data(array_com_protocal)
                i += 1

        except:
            logger.error("send  led color data {}", traceback.format_exc())
            logger.error(list_com[i][0].port)


def display_led_screen():
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


def index_form_last(buffer, char, size_data):
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


def read(com, state_table, start_num, read_size=3, block=False):
    in_len = com.in_waiting
    if in_len >= read_size + 2:
        data_read_buffer = com.read_all()
    else:
        if block:
            data_read_buffer = com.read(read_size + 2)
        else:
            data_read_buffer = com.read_all()
    in_len = len(data_read_buffer)
    if in_len == 0:
        return
    if not in_len % (read_size + 2) != 0:
        if in_len > 2:
            if in_len > read_size + 2:
                data_want = data_read_buffer[in_len - (read_size + 2):]
                in_len = read_size + 2
            else:
                data_want = data_read_buffer
        else:
            return
    else:
        data_want = data_read_buffer
    try:
        index_of_fc = data_want.index(252)
    except ValueError:
        return
    if index_of_fc < in_len - 2:
        start_fc_idx = index_of_fc + 2
        arr_after_fc = data_want[start_fc_idx:]
        len_arr_after_fc = len(arr_after_fc)
        last_num = start_num + read_size - 1
        for i in range(len_arr_after_fc):
            idx = last_num - i
            if idx < 0 or idx >= len(rect_position_arr):
                break
            coors = rect_position_arr[idx]
            state_table[coors[0]][coors[1]] = arr_after_fc[i] == 10

    if index_of_fc > 0:
        arr_before_fc = data_want[:index_of_fc]
        len_arr_before_fc = len(arr_before_fc)
        for i in range(len_arr_before_fc):
            try:
                coors = rect_position_arr[i + start_num]
                state_table[coors[0]][coors[1]] = arr_before_fc[len_arr_before_fc - i - 1] == 10
            except:
                logger.error("data_want:{}; len:{}", str(data_want), len(data_want))
                logger.error("index_of_fc:{}", index_of_fc)
                logger.error("arr_before_fc:{}, len:{}", str(arr_before_fc), len(arr_before_fc))
                logger.error("rect_position_arr:{} len:{}", str(rect_position_arr), len(rect_position_arr))
                logger.error("index in rect_position_arr {}, start_num:{} ", i + start_num, start_num)
                break


def read_new_no_completed(com_obj, rst_arr, start_num, read_size=3, block=False):
    com = com_obj[0].main_engine
    buf_read = com_obj[0].read_date_buffer
    in_len = com.in_waiting
    if in_len >= read_size + 2:
        data_read_buffer = com.read_all()
        in_len = len(data_read_buffer)
        index_of_fc = -1
        for i in range(in_len - 1, -1, -1):
            if data_read_buffer[i] == 252:
                index_of_fc = i
                break

        if index_of_fc != -1:
            pass
        else:
            com_obj[0].read_date_buffer = data_read_buffer.copy()
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


def update_screen_state_by_com_old(layout_type, state_table, state_2array):
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


def update_screen_state_by_com(layout_type, state_table, state_2array):
    for com in list_com:
        values = [
         com[1], com[2]]
        src_idx_start = int(values[0]) - 1
        src_idx_end = int(values[1])
        size = src_idx_end - src_idx_start
        read((com[0].main_engine), state_table, src_idx_start, read_size=size, block=com_is_block)


def clear_com_buffer():
    if com_is_block:
        for com in list_com:
            com[0].main_engine.flushInput()


def update_screen_state_by_com_new(layout_type, state_table):
    if Setting.USE_SERIAL_HD:
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
                read((com[0].main_engine), one_array, src_idx_start, read_size=size, block=com_is_block)
            except:
                logger.error("{} except: {} ", com[0].main_engine.name, traceback.format_exc())

        position_convert.position_convert_1arr_to_2arr(layout_type, one_array, state_table)


def get_led_screen_state():
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
                m_led_state_one_array[i] = data_rst[tmp - i] == 10

        except:
            pass

    position_convert.position_convert_1arr_to_2arr(m_layout_type, m_led_state_one_array, m_led_state_two_array)


def real_led_to_screen_virtual_led_state_switch(table_real_led, table_virtual_led, g_wall_has_been_tread_arr2=None):
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


def update_led(setting, logic_2array, table_state, state_2array, g_wall_has_been_tread_arr2):
    if len(list_com) > 0:
        try:
            logger.debug("update led color")
            draw_screen_by_com(setting, logic_2array)
            logger.debug("end")
            logger.debug("update led state")
            update_screen_state_by_com(setting, table_state, state_2array)
            logger.debug("end")
            logger.debug("data switch")
            real_led_to_screen_virtual_led_state_switch(state_2array, table_state, g_wall_has_been_tread_arr2)
            logger.debug("end")
            return 1
        except:
            logger.error("update_led: {} ", traceback.format_exc())
            return 0


def draw_led_color(setting, logic_2array):
    if len(list_com) > 0:
        logger.debug("update led color")
        try:
            draw_screen_by_com(None, logic_2array)
            return 1
        except:
            logger.error("draw_led_color: {} ", traceback.format_exc())
            return 0

        logger.debug("end")


def get_led_state(setting, table_state, state_2array, g_wall_has_been_tread_arr2):
    if len(list_com) > 0:
        logger.debug("update led state")
        try:
            update_screen_state_by_com(None, table_state, None)
            return 1
        except:
            logger.error("get_led_state: {} ", traceback.format_exc())
            return 0

        logger.debug("end")
    return 0

# okay decompiling /games/climb/climb_source_code/led/led_control.pyc
