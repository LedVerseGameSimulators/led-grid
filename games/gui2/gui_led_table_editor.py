# Source Generated with Decompyle++
# File: gui_led_table_editor.pyc (Python 3.7)

import decimal
import shelve
from tkinter import Menu
import loguru
from gui.language import language as Language
from model.setting import Color as gui_color, Color, Setting
from tkinter import ttk, colorchooser
from gui2.gui_led_canvas2 import gui_led_canvas2 as canvas_led

class LedTable:
    TREAD = 1
    NO_TREAD = 0
    SELECT_COLOR = '#' + '{:02X}'.format(gui_color.WHITE_GREEN[0]) + '{:02X}'.format(gui_color.WHITE_GREEN[1]) + '{:02X}'.format(gui_color.WHITE_GREEN[2])
    WHITE_FORMAT = '#' + '{:02X}'.format(gui_color.WHITE[0]) + '{:02X}'.format(gui_color.WHITE[1]) + '{:02X}'.format(gui_color.WHITE[2])
    BLACK_FORMAT = '#' + '{:02X}'.format(gui_color.BLACK[0]) + '{:02X}'.format(gui_color.BLACK[1]) + '{:02X}'.format(gui_color.BLACK[2])
    YELLOW_FORMAT = '#' + '{:02X}'.format(gui_color.YELLOW[0]) + '{:02X}'.format(gui_color.YELLOW[1]) + '{:02X}'.format(gui_color.YELLOW[2])
    SELECTED = True
    
    def set_color_table(self, row, col, color):
        
        try:
            self.led_table[row][col] = color
        except:
            pass


    
    def set_table_color(self, table, color = (gui_color.WHITE,)):
        table_row = len(table)
        table_col = len(table[0])
        for row in range(table_row):
            for col in range(table_col):
                table[row][col] = color
            
        

    
    def set_table_state(self, table, state = (False,)):
        table_row = len(table)
        table_col = len(table[0])
        for row in range(table_row):
            for col in range(table_col):
                table[row][col] = state
            
        

    
    def clear_led_table(self):
        arr_wall_ligth = self.get_wall_light_arr()
        arr_wall_screen = self.get_wall_screen_arr()
        for i in range(len(arr_wall_ligth)):
            arr_wall_ligth[i] = Color.BLACK
            arr_wall_screen[i] = 0
        
        for i in range(len(self.led_table)):
            for j in range(len(self.led_table[0])):
                self.led_table[i][j] = Color.BLACK
            
        

    
    def set_table_specified_state(self, table, range_in_ij, state = (False,)):
        for i in range(range_in_ij[0][0], range_in_ij[0][1] + 1):
            for j in range(range_in_ij[1][0], range_in_ij[1][1] + 1):
                table[i][j] = state
            
        

    
    def update_led_cell_set_color(self, set_cell, color):
        self.canvas.draw_set_cell(set_cell, color)

    
    def redraw_led_table_default(self, line, draw_canvas = (0, True)):
        for i in range(len(self.led_table)):
            for j in range(len(self.led_table[0])):
                if self.green_table[i][j]:
                    self.led_table[i][j] = gui_color.GREEN
                    self.green_table[i][j] = False
                    if self.red_table[i][j]:
                        self.red_table[i][j] = False
                    if self.tread_short_stay[i][j] is not None:
                        self.tread_short_stay[i][j] = None
                    if self.safe_table[i][j]:
                        self.safe_table[i][j] = False
                    if self.plus_table[i][j] is not None:
                        self.plus_table[i][j] = None
                    if self.deduct_table[i][j]:
                        self.deduct_table[i][j] = False
                    if self.other_color_table[i][j] is not None:
                        self.other_color_table[i][j] = None
                        continue
                        if self.red_table[i][j]:
                            self.led_table[i][j] = gui_color.RED
                            self.red_table[i][j] = False
                            if self.tread_short_stay[i][j] is not None:
                                self.tread_short_stay[i][j] = None
                            if self.safe_table[i][j]:
                                self.safe_table[i][j] = False
                            if self.plus_table[i][j] is not None:
                                self.plus_table[i][j] = None
                            if self.deduct_table[i][j]:
                                self.deduct_table[i][j] = False
                            if self.other_color_table[i][j] is not None:
                                self.other_color_table[i][j] = None
                                continue
                                if self.tread_short_stay[i][j] is not None:
                                    self.led_table[i][j] = self.tread_short_stay[i][j]
                                    self.tread_short_stay[i][j] = None
                                    if self.safe_table[i][j]:
                                        self.safe_table[i][j] = False
                                    if self.plus_table[i][j] is not None:
                                        self.plus_table[i][j] = None
                                    if self.deduct_table[i][j]:
                                        self.deduct_table[i][j] = False
                                    if self.other_color_table[i][j] is not None:
                                        self.other_color_table[i][j] = None
                                        continue
                                        if self.safe_table[i][j]:
                                            self.led_table[i][j] = self.safe_color
                                            self.safe_table[i][j] = False
                                            if self.plus_table[i][j] is not None:
                                                self.plus_table[i][j] = None
                                            if self.deduct_table[i][j]:
                                                self.deduct_table[i][j] = False
                                            if self.other_color_table[i][j] is not None:
                                                self.other_color_table[i][j] = None
                                                continue
                                                if self.plus_table[i][j] is not None:
                                                    self.led_table[i][j] = self.plus_table[i][j]
                                                    self.plus_table[i][j] = None
                                                    if self.deduct_table[i][j]:
                                                        self.deduct_table[i][j] = False
                                                    if self.other_color_table[i][j] is not None:
                                                        self.other_color_table[i][j] = None
                                                        continue
                                                        if self.deduct_table[i][j]:
                                                            self.led_table[i][j] = gui_color.DEDUCT_COLOR
                                                            self.deduct_table[i][j] = False
                                                            if self.other_color_table[i][j] is not None:
                                                                self.other_color_table[i][j] = None
                                                                continue
                                                                if self.other_color_table[i][j] is not None:
                                                                    self.led_table[i][j] = self.other_color_table[i][j]
                                                                    self.other_color_table[i][j] = None
                                                            if draw_canvas and self.canvas is not None:
                                                                self.canvas.draw_led_color(self.led_table)
                                                                self.wall_button_light.draw_led_color([
                                                                    self.wall_light_array])
                                                                self.wall_screen.write_text_by_table([
                                                                    self.wall_screen_array])
                                                                self.canvas.draw_line_in_table(line)

    
    def redraw_led_table_default_bft250610(self, line, draw_canvas = (0, True)):
        for i in range(len(self.led_table)):
            for j in range(len(self.led_table[0])):
                if self.deduct_table[i][j]:
                    self.led_table[i][j] = gui_color.DEDUCT_COLOR
                    self.deduct_table[i][j] = False
                if self.plus_table[i][j] is not None:
                    self.led_table[i][j] = self.plus_table[i][j]
                    self.plus_table[i][j] = None
                if self.other_color_table[i][j] is not None:
                    self.led_table[i][j] = self.other_color_table[i][j]
                    self.other_color_table[i][j] = None
                if self.safe_table[i][j]:
                    self.led_table[i][j] = self.safe_color
                    self.safe_table[i][j] = False
                if self.red_table[i][j]:
                    self.led_table[i][j] = gui_color.RED
                    self.red_table[i][j] = False
                if self.green_table[i][j]:
                    self.led_table[i][j] = gui_color.GREEN
                    self.green_table[i][j] = False
        
        if draw_canvas and self.canvas is not None:
            self.canvas.draw_led_color(self.led_table)
            self.wall_button_light.draw_led_color([
                self.wall_light_array])
            self.wall_screen.write_text_by_table([
                self.wall_screen_array])
            self.canvas.draw_line_in_table(line)

    
    def set_color_table_by_set_cell(self, set_cell, color = (gui_color.BLACK,)):
        dici = None
        
        try:
            if color == gui_color.RED:
                for cell in set_cell:
                    i = round(cell[0], dici)
                    j = round(cell[1], dici)
                    self.red_table[i][j] = True
                
            elif color == self.safe_color:
                for cell in set_cell:
                    i = round(cell[0], dici)
                    j = round(cell[1], dici)
                    self.safe_table[i][j] = True
                
            elif color == gui_color.GREEN:
                for cell in set_cell:
                    i = round(cell[0], dici)
                    j = round(cell[1], dici)
                    self.green_table[i][j] = True
                
            elif color == gui_color.DEDUCT_COLOR:
                for cell in set_cell:
                    i = round(cell[0], dici)
                    j = round(cell[1], dici)
                    self.deduct_table[i][j] = True
                
            elif color in gui_color.PLUS_ARR:
                for cell in set_cell:
                    i = round(cell[0], dici)
                    j = round(cell[1], dici)
                    self.plus_table[i][j] = color
                
            else:
                for cell in set_cell:
                    i = round(cell[0], dici)
                    j = round(cell[1], dici)
                    self.other_color_table[i][j] = color
        except:
            loguru.logger.error('mey be out of range')
        


    
    def draw_led_table_text_by_group(self, group):
        if self.canvas is not None:
            
            try:
                data = group.start_member
                i = 0
                for cell in data:
                    self.canvas.write_text_in_table(cell, group.text[i])
                    i += 1
            except:
                pass


    
    def clear_screen_text(self, group = (None,)):
        if self.canvas is not None:
            if group is not None:
                data = group.start_member
                for cell in data:
                    self.canvas.write_text_in_table(cell)
                
            else:
                for cell in self.wall_screen_table:
                    self.canvas.write_text_in_table(cell)
                

    
    def draw_led_table_with_cell_set_color(self, set_cell, color = (gui_color.WHITE_FORMAT,)):
        for coors in set_cell:
            self.led_table[round(coors[0])][round(coors[1])] = color
        
        self.canvas.draw_led_table_color(self.led_table)

    
    def draw_color(self, line = (None,)):
        if self.canvas:
            self.canvas.draw_led_color(self.led_table)
            self.wall_button_light.draw_led_color([
                self.wall_light_array])
            self.wall_screen.write_text_by_table([
                self.wall_screen_array])
            if line:
                self.canvas.draw_line_in_table(line)

    
    def set_color_of_area_select(self):
        color_not_255 = [
            0,
            1,
            2]
        tp_color = colorchooser.askcolor()
        tp_color = tp_color[0]
        for i in range(3):
            if int(tp_color[i]) == 255:
                color_not_255[i] = 254
                continue
            color_not_255[i] = int(tp_color[i])
        
        return color_not_255

    
    def start_move(self, event):
        self.canvas.clear_table_color(self.on_cur_select_table)
        self.first_x = event.x
        self.first_y = event.y
        self.mouse_led_coor_start = self.canvas.screen_coord_to_led_coord((self.first_x, self.first_y))
        self.mouse_led_coor_end = [
            self.mouse_led_coor_start[0],
            self.mouse_led_coor_start[1]]
        self.mouse_screen_coor_start = self.canvas.led_coord_to_screen_coord(self.mouse_led_coor_start)
        self.last_click_select_start = self.mouse_led_coor_start
        self.last_click_select_end = self.mouse_led_coor_end
        i = self.mouse_led_coor_start[0]
        j = self.mouse_led_coor_start[1]
        tmp_end = self.canvas.led_coord_to_screen_coord((i + 1, j + 1))
        self.canvas.canvas.coords('L', self.mouse_screen_coor_start[1], self.mouse_screen_coor_start[0], tmp_end[1], tmp_end[0])

    
    def start_move_ctrl(self, event):
        self.first_x = event.x
        self.first_y = event.y
        self.mouse_led_coor_start = self.canvas.screen_coord_to_led_coord((self.first_x, self.first_y))
        self.mouse_led_coor_end = [
            self.mouse_led_coor_start[0],
            self.mouse_led_coor_start[1]]
        self.mouse_screen_coor_start = self.canvas.led_coord_to_screen_coord(self.mouse_led_coor_start)
        self.last_click_select_start = self.mouse_led_coor_start
        self.last_click_select_end = self.mouse_led_coor_end
        i = self.mouse_led_coor_start[0]
        j = self.mouse_led_coor_start[1]
        tmp_end = self.canvas.led_coord_to_screen_coord((i + 1, j + 1))
        self.canvas.canvas.coords('L', self.mouse_screen_coor_start[1], self.mouse_screen_coor_start[0], tmp_end[1], tmp_end[0])

    
    def stop_move(self, event):
        self.set_table_specified_state(self.on_cur_select_table, ((self.last_click_select_start[0], self.last_click_select_end[0]), (self.last_click_select_start[1], self.last_click_select_end[1])), LedTable.SELECTED)

    
    def on_move(self, event):
        self.canvas.set_table_specified_color(((self.last_click_select_start[0], self.last_click_select_end[0]), (self.last_click_select_start[1], self.last_click_select_end[1])), LedTable.WHITE_FORMAT)
        pos_end = self.canvas.screen_coord_to_led_coord((event.x, event.y))
        tmp_row_min = min(self.mouse_led_coor_start[0], pos_end[0])
        tmp_row_max = max(self.mouse_led_coor_start[0], pos_end[0])
        tmp_col_min = min(self.mouse_led_coor_start[1], pos_end[1])
        tmp_col_max = max(self.mouse_led_coor_start[1], pos_end[1])
        tmp_start = self.canvas.led_coord_to_screen_coord((tmp_row_min, tmp_col_min))
        tmp_end = self.canvas.led_coord_to_screen_coord((tmp_row_max + 1, tmp_col_max + 1))
        self.last_click_select_start = (tmp_row_min, tmp_col_min)
        self.last_click_select_end = (tmp_row_max, tmp_col_max)
        self.canvas.canvas.coords('L', tmp_start[1], tmp_start[0], tmp_end[1], tmp_end[0])
        for i in range(tmp_row_min, tmp_row_max + 1):
            for j in range(tmp_col_min, tmp_col_max + 1):
                self.canvas.canvas.itemconfig(self.canvas.arr2[i][j], LedTable.SELECT_COLOR, **('fill',))
            
        

    
    def screen_mouse_event(self, event, state = ('down',)):
        if state == 'down':
            pos = self.canvas.screen_coord_to_led_coord((event.x, event.y))
            state = LedTable.TREAD
        else:
            pos = self.canvas.screen_coord_to_led_coord((event.x, event.y))
            state = LedTable.NO_TREAD
        row = pos[0]
        col = pos[1]
        self.led_coors_click = ((row, col), state)

    
    def screen_mouse_event_wall_table(self, event, state = ('down',)):
        if state == 'down':
            pos = self.canvas.screen_coord_to_led_coord((event.x, event.y))
            state = LedTable.TREAD
        else:
            pos = self.canvas.screen_coord_to_led_coord((event.x, event.y))
            state = LedTable.NO_TREAD
        row = pos[0]
        col = pos[1]
        self.led_coors_click_wall = ((row, col), state)

    
    def get_cur_select_cell_set(self):
        set_cell = set()
        for i in range(len(self.on_cur_select_table)):
            for j in range(len(self.on_cur_select_table[0])):
                if self.on_cur_select_table[i][j]:
                    set_cell.add((i, j))
        
        return set_cell

    
    def create_right_button_menu(self, root):
        menu_right_button = Menu(root)
        None(None, (lambda event = None: self.menupop(event, menu_right_button)))

    
    def menupop(self, event, menu):
        led_coor = self.canvas.screen_coord_to_led_coord((event.x, event.y))
        if self.on_cur_select_table[led_coor[0]][led_coor[1]] == LedTable.SELECTED:
            menu.post(event.x_root, event.y_root)

    
    def get_wall_light_table(self):
        return self.wall_light_table

    
    def get_led_table(self):
        for i in range(len(self.led_table)):
            for j in range(len(self.led_table[0])):
                str_t = self.led_table[i][j]
                tuple_tmp = (int(str_t[1:3], 16, **('base',)), int(str_t[3:5], 16, **('base',)), int(str_t[5:7], 16, **('base',)))
                self.tmp_led_table[i][j] = tuple_tmp
            
        
        return self.tmp_led_table

    
    def get_state_table(self):
        return self.table_state

    
    def get_state_2array(self):
        return self.state_2array

    
    def get_g_wall_has_been_tread_arr2(self):
        return self.g_wall_has_been_tread_arr2

    
    def get_wall_light_arr(self):
        return self.wall_light_array

    
    def get_wall_screen_arr(self):
        return self.wall_screen_array

    
    def get_wall_light_state_array(self):
        return self.wall_light_state_array

    
    def get_canvas_table_size(self):
        if self.canvas:
            return self.canvas.size
        return [
            None,
            0]

    
    def screen_mouse_click_state_get(self):
        if self.canvas:
            
            try:
                coors_click = self.led_coors_click
                self.table_state[coors_click[0][0]][coors_click[0][1]] = coors_click[1]
                coors_click = self.led_coors_click_wall
                self.wall_light_state_array[coors_click[0][1]] = coors_click[1]
            except:
                pass


    
    def __init__(self, root, wall_light_arr_len, ui_table_row, ui_table_col, table_display = (None,)):
        high = ui_table_row
        width = ui_table_col
        self.row = high
        self.col = width
        self.led_coors_click = ((0, 0), 0)
        self.led_coors_click_wall = ((0, 0), 0)
        self.state_2array = (lambda _iter_ = None: [ [
5] * width for _ in .0 ])(range(high))
        self.table_state = (lambda _iter_ = None: [ [
False] * width for _ in .0 ])(range(high))
        self.g_wall_has_been_tread_arr2 = (lambda _iter_ = None: [ [
False] * width for _ in .0 ])(range(high))
        self.wall_light_array = [
            gui_color.BLACK] * wall_light_arr_len
        self.wall_light_state_array = [
            False] * wall_light_arr_len
        self.wall_screen_array = [
            0] * wall_light_arr_len
        self.tmp_led_table = (lambda _iter_ = None: [ [
gui_color.WHITE] * width for _ in .0 ])(range(high))
        self.led_table = (lambda _iter_ = None: [ [
gui_color.BLACK] * width for _ in .0 ])(range(high))
        self.red_table = (lambda _iter_ = None: [ [
False] * width for _ in .0 ])(range(high))
        self.green_table = (lambda _iter_ = None: [ [
False] * width for _ in .0 ])(range(high))
        self.safe_table = (lambda _iter_ = None: [ [
False] * width for _ in .0 ])(range(high))
        self.safe_color = None
        self.deduct_table = (lambda _iter_ = None: [ [
False] * width for _ in .0 ])(range(high))
        self.plus_table = (lambda _iter_ = None: [ [
None] * width for _ in .0 ])(range(high))
        self.other_color_table = (lambda _iter_ = None: [ [
None] * width for _ in .0 ])(range(high))
        self.tread_short_stay = (lambda _iter_ = None: [ [
None] * width for _ in .0 ])(range(high))
        self.last_trigger_span = (lambda _iter_ = None: [ [
0] * width for _ in .0 ])(range(high))
        self.on_cur_select_table = (lambda _iter_ = None: [ [
bool] * width for _ in .0 ])(range(high))
        if table_display is None:
            fm_wall = ttk.Frame(root)
            fm_wall.pack()
            fm_her2 = ttk.Frame(root)
            fm_her2.pack()
            f = shelve.open('./setting/debug_parameter')
            game_display = f.get('game_display')
            f.close()
        else:
            game_display = table_display
        self.canvas = None
        if game_display:
            led_title_her = canvas_led.CanvasLed(fm_wall, 1, wall_light_arr_len, None)
            led_title_her.canvas.pack('top', **('side',))
            led_title_her.write_serial_num_in_rectangle(0, **('direct',))
            wall_screen = canvas_led.CanvasLed(fm_wall, 1, wall_light_arr_len, None)
            wall_screen.canvas.pack('top', **('side',))
            wall_screen.create_canvas_text_arr()
            wall_button_light = canvas_led.CanvasLed(fm_wall, 1, wall_light_arr_len, None)
            wall_button_light.canvas.pack('top', **('side',))
            None(None, (lambda event = None: self.screen_mouse_event_wall_table(event, 'down')))
            None(None, (lambda event = None: self.screen_mouse_event_wall_table(event, 'up')))
            self.wall_button_light = wall_button_light
            self.wall_screen = wall_screen
            led_canvas = canvas_led.CanvasLed(fm_her2, high, width, None)
            canvas = led_canvas.canvas
            canvas.pack('left', 'both', **('side', 'fill'))
            None(None, (lambda event = None: self.screen_mouse_event(event, 'down')))
            None(None, (lambda event = None: self.screen_mouse_event(event, 'up')))
            self.canvas = led_canvas
            self.canvas.canvas.create_rectangle(0, 0, 0, 0, 'L', 'black', **('tags', 'outline'))


