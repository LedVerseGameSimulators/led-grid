# Source Generated with Decompyle++
# File: Play.pyc (Python 3.7)

import sys
import time
import traceback
from model.setting import Setting, Color
from loguru import logger

class Play:
    ACCURACY = 1e-06
    MAX_TIME = 3600
    
    def get_game_speed(self, game_level, leval_span):
        game_level_speed = 1  # default — decompiler omits this
        if game_level <= 1:
            game_level_speed = 1 - leval_span
            if game_level_speed < 0:
                game_level_speed = 0.1
        elif game_level == 2:
            game_level_speed = 1
        else:
            game_level_speed = 1 + leval_span
        return game_level_speed
    def __init__(self, obj_led_table, setting, partial_fun_cb, game_level, is_game_living = (None, None, 1, True)):
        self.total_pass = 0
        self.game_level_speed = 1
        game_level = game_level
        if setting:
            leval_span = setting.leval_span.get()
            self.blue_hide_max_time = setting.blue_hide_max_time.get()
            self.wall_line = setting.corner_line_start.get()
            self.game_level_speed = self.get_game_speed(game_level, leval_span)
        self.last_time = time.time()
        self.current_time = time.time()
        self.running_state = True
        self.is_game_living = is_game_living
        self.obj_led_table = obj_led_table
        self.callback = partial_fun_cb

    
    def stop_running(self):
        self.running_state = False

    
    def deal_all_direction(self, group):
        """Move group one step in group.direct, clipped to group.activity_area.
        Returns (new_direction, new_start_member).
        Ported from LED-Hex working implementation — replaces broken decompiled version.
        """
        direct = group.direct

        _DELTA = {
            Setting.UP:         (-1,  0),
            Setting.DOWN:       ( 1,  0),
            Setting.LEFT:       ( 0, -1),
            Setting.RIGHT:      ( 0,  1),
            Setting.LEFT_UP:    (-1, -1),
            Setting.RIGHT_UP:   (-1,  1),
            Setting.LEFT_DOWN:  ( 1, -1),
            Setting.RIGHT_DOWN: ( 1,  1),
        }

        _REVERSE = {
            Setting.UP:         Setting.DOWN,
            Setting.DOWN:       Setting.UP,
            Setting.LEFT:       Setting.RIGHT,
            Setting.RIGHT:      Setting.LEFT,
            Setting.LEFT_UP:    Setting.RIGHT_DOWN,
            Setting.RIGHT_DOWN: Setting.LEFT_UP,
            Setting.LEFT_DOWN:  Setting.RIGHT_UP,
            Setting.RIGHT_UP:   Setting.LEFT_DOWN,
        }

        if direct not in _DELTA:
            return (direct, list(group.start_member) if group.start_member else [])

        cells = list(group.start_member)
        if not cells:
            return (direct, [])

        dr, dc = _DELTA[direct]
        area = group.activity_area
        row_from, row_to = area[0]
        col_from, col_to = area[1]

        def _in(nr, nc):
            return row_from <= nr < row_to and col_from <= nc < col_to

        moved = [(c[0] + dr, c[1] + dc) for c in cells]

        # No edge hit: whole group advances rigidly.
        if all(_in(nr, nc) for nr, nc in moved):
            return (direct, moved)

        # An edge is hit. Behavior depends on edge_run_into.
        edge = getattr(group, "edge_run_into", Setting.BACK)

        if edge in (Setting.DISAPPEAR, Setting.SLOW_DISAPPEAR):
            # Cells leaving the area vanish; the rest advance.
            kept = [(nr, nc) for nr, nc in moved if _in(nr, nc)]
            return (direct, kept)

        # BACK (and default): RIGID BOUNCE — reverse direction and move the
        # whole pattern, preserving every cell (no width erosion). If the
        # reversed move also overflows (pattern wider than area), just flip
        # direction and hold position this frame.
        ndirect = _REVERSE.get(direct, direct)
        ndr, ndc = _DELTA.get(ndirect, (0, 0))
        rmoved = [(c[0] + ndr, c[1] + ndc) for c in cells]
        if all(_in(nr, nc) for nr, nc in rmoved):
            return (ndirect, rmoved)
        return (ndirect, cells)
    def group_in_time(self, start_time, end_time):
        tmp_total = self.total_pass
        if not tmp_total - start_time >= Play.ACCURACY:
            pass
        bigger = tmp_total - start_time >= -(Play.ACCURACY)
        smaller = end_time - tmp_total > Play.ACCURACY
        if bigger:
            pass
        return smaller

    
    def smaller(self, num1, num2):
        smer = num2 - num1 > Play.ACCURACY
        return smer

    
    def clear_led_table(self, color=Color.BLACK):
        obj_led_table = self.obj_led_table
        led_table = obj_led_table.led_table
        arr_wall_light = obj_led_table.get_wall_light_arr()
        arr_wall_screen = obj_led_table.get_wall_screen_arr()
        for i in range(len(arr_wall_light)):
            arr_wall_light[i] = color
            arr_wall_screen[i] = 0
        
        for i in range(len(led_table)):
            for j in range(len(led_table[0])):
                led_table[i][j] = color
            
        

    
    def check_blue_will_be_cover_over_times_old(self, dict_group, time_cur):
        o_led_table = self.obj_led_table
        time_threshold = self.blue_hide_max_time
        list_group = dict_group.values()
        coors_list = []
        for group in list_group:
            if not group.type == Setting.FLOOR_LIGHT or group.color == Color.RED:
                if group.color == Color.GREEN and group.speed == 0 and group.start_time_sec < time_cur:
                    for cell in group.start_member:
                        i = round(cell[0])
                        j = round(cell[1])
                        if not o_led_table.blue_table[i][j] or o_led_table.red_table[i][j]:
                            if o_led_table.green_table[i][j]:
                                time_bet = group.end_time_sec - time_cur
                                if time_bet > time_threshold:
                                    coors_list.append((i, j))
                            for group in list_group:
                                if group.type == Setting.FLOOR_LIGHT and group.color == Color.BLUE and group.speed == 0:
                                    for cell in group.start_member.copy():
                                        i = round(cell[0])
                                        j = round(cell[1])
                                        if not o_led_table.blue_table[i][j] or o_led_table.red_table[i][j]:
                                            if o_led_table.green_table[i][j] and cell in coors_list:
                                                group.start_member.remove(cell)
                                        return None

    
    def update(self, dict_group, time_pass = (0,)):
        o_led_table = self.obj_led_table
        total_pass = self.total_pass
        self.clear_led_table()
        for key, value in dict_group.items():
            group = value
            set_cell = group.start_member
            if set_cell is not None and self.group_in_time(group.start_time_sec, group.end_time_sec) or group.type == Setting.FLOOR_LIGHT:
                o_led_table.set_color_table_by_set_cell(set_cell, group.color)
            elif group.type == Setting.SCREEN_LIGHT:
                
                try:
                    i = 0
                    for index in group.start_member:
                        o_led_table.get_wall_screen_arr()[index] = group.text[i]
                        i += 1
                except:
                    logger.error('running update wall screen arr text', traceback.format_exc())

            else:
                i = 0
                
                try:
                    for index in group.start_member:
                        o_led_table.get_wall_light_arr()[index] = group.color
                        i += 1
                except:
                    logger.error('running update wall button light arr', traceback.format_exc())

        
        if self.callback:
            ret = self.callback(self, self.dict_group, time_pass, total_pass)
            if not ret:
                self.stop_running()

    
    def running(self, dict_group):
        """Main game loop — ported from led-climb / LED-Hex working implementation.
        Replaces broken decompiled version (missing move_distance gate caused every
        moving group to advance one cell every frame ~100× too fast).
        """
        logger.info('editor game running by time')
        self.dict_group = dict_group
        self.running_state = True
        self.last_time = time.time()
        self.total_pass = 0
        floor_light_state = self.obj_led_table.get_state_table()
        wall_light_state = self.obj_led_table.get_wall_light_state_array()
        while self.running_state and self.is_game_living:
            self.current_time = time.time()
            time_pass = self.current_time - self.last_time
            self.last_time = self.current_time
            self.total_pass += time_pass
            for key, value in self.dict_group.items():
                group = value
                change = 0
                last_speed = 0
                if group.speed != 0:
                    last_speed = 1 / group.speed * self.game_level_speed
                    change = last_speed * time_pass
                start_time = group.start_time_sec
                end_time = group.end_time_sec
                if self.group_in_time(start_time, end_time):
                    if last_speed != 0:
                        tmp_time = self.total_pass - start_time
                        if tmp_time < time_pass:
                            change = tmp_time * last_speed
                        group.move_distance += change
                        if self.smaller(group.move_distance, 1):
                            continue
                        group.move_distance -= 1
                        direction_current, set_cell_current = self.deal_all_direction(group)
                        group.start_member = set_cell_current
                        group.direct = direction_current
                        self.dict_group[key] = group

            self.update(dict_group, time_pass)

    
    def running_by_blue(self, dict_group):
        logger.info('editor game running by blue')
        self.dict_group = dict_group
        self.running_state = True
        self.last_time = time.time()
        self.total_pass = 0
        self.real_time_pass = 0
        period_check_blue_exist = 2
        self.check_count_time = 0
        self.is_blue_exist = False
        no_sore_arr = (Color.GREEN, Color.RED, self.obj_led_table.safe_color, Color.BLACK, Color.DEDUCT_COLOR)
        floor_light_state = self.obj_led_table.get_state_table()
        floor_light_color = self.obj_led_table.led_table
        wall_light_state = self.obj_led_table.get_wall_light_state_array()
        while self.running_state and self.is_game_living:
            self.current_time = time.time()
            time_pass = self.current_time - self.last_time
            self.last_time = self.current_time
            r = 0
            c = 1
            self.total_pass += time_pass
            self.check_count_time += time_pass
            next_blue_group_start = Play.MAX_TIME
            if self.check_count_time > period_check_blue_exist:
                self.check_count_time = 0
                for key, value in self.dict_group.items():
                    group = value
                    if (group.color in Color.PLUS_ARR and len(group.start_member) > 0 or self.total_pass >= group.start_time_sec) and self.total_pass < group.end_time_sec:
                        next_blue_group_start = self.total_pass
                        break
                    if self.total_pass < group.start_time_sec and group.start_time_sec < next_blue_group_start:
                        next_blue_group_start = group.start_time_sec
                self.total_pass = next_blue_group_start
            for key, value in self.dict_group.items():
                group = value
                set_cell = group.start_member
                change = 0
                last_speed = 0
                if group.speed != 0:
                    last_speed = (1 / group.speed) * self.game_level_speed
                    change = last_speed * time_pass
                if self.group_in_time(group.start_time_sec, group.end_time_sec) or last_speed != 0:
                    tmp_time = self.total_pass - group.start_time_sec
                    if tmp_time < time_pass:
                        change = tmp_time * last_speed
                group.move_distance += change
                (direction_current, set_cell_current) = self.deal_all_direction(group)
                group.start_member = set_cell_current
                group.direct = direction_current
                self.dict_group[key] = group
            
            self.update(dict_group, time_pass)
            if time_pass >= 0.3:
                logger.warning('bad game frame frequency:' + str(time_pass))
            return None

    
    def running_new(self, dict_group, game, idle, delay_time, parent = (False, 0, None)):
        self.running_state = True
        self.last_time = time.time()
        self.total_pass = 0
        self.real_time_pass = 0
        period_check_blue_exist = 2
        max_time = 3600
        self.check_count_time = 0
        self.is_blue_exist = False
        time_start = time.time()
        self.start_running = False
        floor_light_state = self.obj_led_table.get_state_table()
        wall_light_state = self.obj_led_table.get_wall_light_state_array()
        while self.running_state:
            self.current_time = time.time()
            if self.start_running:
                self.row_range = (game.zone_row_from, game.zone_row_to)
                self.col_range = (game.zone_col_from, game.zone_col_to)
                self.dict_group = dict_group
                time_pass = self.current_time - self.last_time
                self.last_time = self.current_time
                r = 0
                c = 1
                self.total_pass += time_pass
                self.check_count_time += time_pass
                next_blue_group_start = Play.MAX_TIME
                if game.play_order and self.check_count_time > period_check_blue_exist:
                    self.check_count_time = 0
                    for key, value in self.dict_group.items():
                        group = value
                        if (group.color == Color.BLUE and len(group.start_member) > 0 or self.total_pass >= group.start_time_sec) and self.total_pass < group.end_time_sec:
                            next_blue_group_start = self.total_pass
                            break
                        if self.total_pass < group.start_time_sec and group.start_time_sec < next_blue_group_start:
                            next_blue_group_start = group.start_time_sec
                            print('next_blue_group_start', next_blue_group_start)
                    self.total_pass = next_blue_group_start
                    print(' self.total_pass', int(self.total_pass))
                for key, value in self.dict_group.items():
                    group = value
                    set_cell = group.start_member
                    last_direction = group.direct
                    change = 0
                    last_speed = 0
                    if group.speed != 0:
                        last_speed = (1 / group.speed) * self.game_level_speed
                        change = last_speed * time_pass
                    if self.group_in_time(group.start_time_sec, group.end_time_sec) or last_speed != 0:
                        tmp_time = self.total_pass - group.start_time_sec
                        if tmp_time < time_pass:
                            change = tmp_time * last_speed
                    group.move_distance += change
                    (direction_current, set_cell_current) = self.deal_all_direction(group)
                    group.start_member = set_cell_current
                    group.direct = direction_current
                    self.dict_group[key] = group
                
                parent.update_draw_led_table_idle_game(self.dict_group, self.total_pass, time_pass, **('total_pass', 'time_pass'))
            elif self.current_time - time_start > delay_time and game is not None:
                self.start_running = True
                self.last_time = time.time()
            else:
                time.sleep(0.03)
            logger.debug('one circle')

    
    def running_once(self, dict_group, time_pass):
        self.total_pass += time_pass
        o_led_table = self.obj_led_table
        for key, value in dict_group.items():
            group = value
            set_cell = group.start_member
            change = 0
            last_speed = 0
            if group.speed != 0:
                last_speed = (1 / group.speed) * self.game_level_speed
                change = last_speed * time_pass
            start_time = group.start_time_sec
            end_time = group.end_time_sec
            if self.group_in_time(start_time, end_time) or last_speed != 0:
                tmp_time = self.total_pass - start_time
                if tmp_time < time_pass:
                    change = tmp_time * last_speed
            group.move_distance += change
            (direction_current, set_cell_current) = self.deal_all_direction(group)
            group.start_member = set_cell_current
            group.direct = direction_current
            dict_group[key] = group
            if group.type == Setting.FLOOR_LIGHT:
                o_led_table.set_table_color(o_led_table.led_table, Color.BLACK)
                o_led_table.set_color_table_by_set_cell(set_cell, group.color)
                o_led_table.redraw_led_table_default(False, **('draw_canvas',))


