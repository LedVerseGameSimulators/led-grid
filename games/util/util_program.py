# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: util_program.py
import decimal, shelve, time
from decimal import Decimal
from loguru import logger
import led.led_control as led_control
import util.util_program as util_program
g_last_game_over = 0
GAME_SNAKE = 1
GAME_BRIDGE = 2
GAME_HIDE = 3
GAME_MOVE = 4
GAME_MOVE_AGAIN = 5
GAME_TENNIS = 6
GAME_ESCAPE = 7
GAME_LINK = 8
GAME_DISPLAY_UNIT_SIZE = 14

def a_game_is_over(g_audio, root, led_control, blood, game_name=0, info=None):
    global g_last_game_over
    f = shelve.open("./setting/program_params")
    if game_name == GAME_SNAKE:
        f["program_params_snake"] = info
    else:
        if game_name == GAME_BRIDGE:
            f["program_params_bridge"] = info
        else:
            if game_name == GAME_HIDE:
                f["program_params_hide"] = info
            else:
                if game_name == GAME_MOVE:
                    f["program_params_move"] = info
                else:
                    if game_name == GAME_MOVE_AGAIN:
                        f["program_params_move_again"] = info
                    else:
                        if game_name == GAME_TENNIS:
                            f["program_params_tennis"] = info
                        else:
                            if game_name == GAME_ESCAPE:
                                f["program_params_escape"] = info
                            else:
                                if game_name == GAME_LINK:
                                    f["program_params_link"] = info
                                else:
                                    f.close()
                                    logger.debug("audio is stop")
                                    if blood >= 0:
                                        g_last_game_over = 1
                                    else:
                                        g_last_game_over = 1
                                root.destroy()
                                led_control.close_com()
                                g_audio.stop()


def waiting_for_the_last_audio_finished(g_audio, root):
    while True:
        if not g_audio.get_busy():
            time.sleep(0.2)
            break
        root.update()


def get_area_state(row=(), col=(), table_state=None):
    for i in range(row[0] - 1, row[1]):
        for j in range(col[0] - 1, col[1]):
            if table_state[i][j] is True:
                return True


def get_unsafe_area_state(row=(), col=(), table_state=None, safe_area_coords=None):
    for i in range(row[0] - 1, row[1]):
        for j in range(col[0] - 1, col[1]):
            if table_state[i][j] is True and (i, j) not in safe_area_coords:
                return True


def update_led(layout_type, logic_2array, state_2array, table_state, g_wall_has_been_tread_arr2):
    led_control.draw_screen_by_com(layout_type, logic_2array)
    led_control.update_screen_state_by_com(layout_type, table_state, state_2array)
    led_control.real_led_to_screen_virtual_led_state_switch(state_2array, table_state, g_wall_has_been_tread_arr2)


def waiting_for_the_area_tread(area, root_ui, table_state, layout_type, logic_2array, state_2array, g_wall_has_been_tread_arr2):
    while True:
        if get_area_state(area[0], area[1], table_state):
            break
        if not ParaTable.VIRTUAL_EVENT_BY_MOUSE:
            update_led(layout_type, logic_2array, state_2array, table_state, g_wall_has_been_tread_arr2)
        root_ui.update()
        time.sleep(0.2)

    return True


def update_last_color_table(color_table_new, color_table_last):
    for i in range(len(color_table_new)):
        for j in range(len(color_table_new[i])):
            color_table_last[i][j] = color_table_new[i][j]


class ParaTable:
    LEFT_TOP = 0
    RIGHT_TOP = 1
    LEFT_DOWN = 3
    RIGHT_DOWN = 4
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    LEFT_TOP_RIGHT = 0
    LEFT_TOP_DOWN = 1
    RIGHT_TOP_LEFT = 2
    RIGHT_TOP_DOWN = 3
    LEFT_DOWN_RIGHT = 4
    LEFT_DOWN_UP = 5
    RIGHT_DOWN_LEFT = 6
    RIGHT_DOWN_UP = 7
    INC = 1
    DEC = -1
    ROW = 0
    COL = 1
    VIRTUAL_EVENT_BY_MOUSE = False

    def __init__(self, position_type, row, col, group_member_num):
        self.type = position_type
        self.row = row
        self.col = col
        self.group_member_num = group_member_num


def led_square_position_and_num(length, red_square_length, green_square_length):
    """
    length - (green_square_length * n  + red_square_length * (n -1)) / 2 <= red_square_length
    l - (ng + nr - r) <= 2*r
    l - n(g+r) + r <= 2 *r
    (l - r)/(g+r) <= n
    """
    n = (length - red_square_length) / (green_square_length + red_square_length)
    n = int(Decimal(n).quantize((Decimal("0")), rounding=(decimal.ROUND_UP)))
    start = (length - (green_square_length * n + red_square_length * (n - 1))) / 2
    start = int(Decimal(start).quantize((Decimal("0")), rounding=(decimal.ROUND_HALF_UP)))
    return [start, n]

# okay decompiling /games/climb/climb_source_code/util/util_program.pyc
