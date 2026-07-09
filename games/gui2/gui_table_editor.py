# Source Generated with Decompyle++
# File: gui_table_editor.pyc (Python 3.7)

import decimal
import shelve
from tkinter import Menu
from gui.language import language as Language
from model.setting import Color as gui_color, Color, Setting
from tkinter import ttk, colorchooser
from gui2.gui_led_canvas2 import gui_led_canvas2 as canvas_led

class TableEditor:
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
            
        

    
    def set_table_specified_state(self, table, range_in_ij, state = (False,)):
        for i in range(range_in_ij[0][0], range_in_ij[0][1] + 1):
            for j in range(range_in_ij[1][0], range_in_ij[1][1] + 1):
                table[i][j] = state
            
        

    
    def update_led_cell_set_color(self, set_cell, color):
        for cell in set_cell:
            self.led_table[cell[0]][cell[1]] = color
        
        self.canvas.draw_set_cell(set_cell, color)

    
    def draw_table_cell_color(self, cell, color):
        self.led_table[cell[0]][cell[1]] = color
        self.canvas.draw_table_cell(cell, color)

    
    def draw_table_color(self):
        self.canvas.draw_led_color(self.led_table)

    
    def write_text_in_table_cell(self, cell, text):
        self.led_table_text[cell[0]][cell[1]] = text
        self.canvas.write_text_in_table(cell, text)

    
    def write_text_in_table(self):
        self.canvas.write_text_by_table(self.led_table_text)

    
    def redraw_led_table_default(self):
        for i in range(len(self.led_table)):
            for j in range(len(self.led_table[0])):
                if self.blue_table[i][j]:
                    self.led_table[i][j] = gui_color.BLUE
                    self.blue_table[i][j] = False
                if self.red_table[i][j]:
                    self.led_table[i][j] = gui_color.RED
                    self.red_table[i][j] = False
                if self.green_table[i][j]:
                    self.led_table[i][j] = gui_color.GREEN
                    self.green_table[i][j] = False
        
        if self.canvas is not None:
            self.canvas.draw_led_color(self.led_table)
            self.wall_button_light.draw_led_color([
                self.wall_light_array])
            self.wall_screen.write_text_by_table([
                self.wall_screen_array])

    
    def set_color_table_by_set_cell(self, set_cell, color = (gui_color.BLACK,)):
        
        try:
            if color == gui_color.BLUE:
                for cell in set_cell:
                    i = round(cell[0])
                    j = round(cell[1])
                    self.blue_table[i][j] = True
                
            elif color == gui_color.RED:
                for cell in set_cell:
                    i = round(cell[0])
                    j = round(cell[1])
                    self.red_table[i][j] = True
                
            elif color == gui_color.GREEN:
                for cell in set_cell:
                    i = round(cell[0])
                    j = round(cell[1])
                    self.green_table[i][j] = True
                
            else:
                for cell in set_cell:
                    i = round(cell[0])
                    j = round(cell[1])
                    self.led_table[i][j] = color
        except:
            print('mey be out of range')
        


    
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
        
        print(color_not_255)
        return color_not_255

    
    def update_table(self):
        self.draw_table_color()
        self.write_text_in_table()

    
    def start_move(self, event):
        self.screen_mouse_event(event, 'down')
        print('running move button left press down')
        self.canvas.clear_table_color(self.on_cur_select_table)
        self.draw_table_color()
        self.first_x = event.x
        self.first_y = event.y
        self.mouse_led_coor_start = self.canvas.screen_coord_to_led_coord((self.first_x, self.first_y))
        self.mouse_led_coor_end = [
            self.mouse_led_coor_start[0],
            self.mouse_led_coor_start[1]]
        self.mouse_screen_coor_start = self.canvas.led_coord_to_screen_coord(self.mouse_led_coor_start)
        self.last_click_select_start = self.mouse_led_coor_start
        self.last_click_select_end = self.mouse_led_coor_end
        print('first position', self.first_x, self.first_y)
        print('running led coords', self.mouse_led_coor_start[0], self.mouse_led_coor_start[1])
        print('running event.y event.x ', event.y, event.x)
        i = self.mouse_led_coor_start[0]
        j = self.mouse_led_coor_start[1]
        tmp_end = self.canvas.led_coord_to_screen_coord((i + 1, j + 1))
        self.canvas.canvas.coords('L', self.mouse_screen_coor_start[1], self.mouse_screen_coor_start[0], tmp_end[1], tmp_end[0])

    
    def start_move_ctrl(self, event):
        print('running move, button left + Ctrl press down')
        self.first_x = event.x
        self.first_y = event.y
        self.mouse_led_coor_start = self.canvas.screen_coord_to_led_coord((self.first_x, self.first_y))
        self.mouse_led_coor_end = [
            self.mouse_led_coor_start[0],
            self.mouse_led_coor_start[1]]
        self.mouse_screen_coor_start = self.canvas.led_coord_to_screen_coord(self.mouse_led_coor_start)
        self.last_click_select_start = self.mouse_led_coor_start
        self.last_click_select_end = self.mouse_led_coor_end
        print('first position', self.first_x, self.first_y)
        print('running led coords', self.mouse_led_coor_start[0], self.mouse_led_coor_start[1])
        print('running event.y event.x ', event.y, event.x)
        i = self.mouse_led_coor_start[0]
        j = self.mouse_led_coor_start[1]
        tmp_end = self.canvas.led_coord_to_screen_coord((i + 1, j + 1))
        self.canvas.canvas.coords('L', self.mouse_screen_coor_start[1], self.mouse_screen_coor_start[0], tmp_end[1], tmp_end[0])

    
    def stop_move(self, event):
        self.screen_mouse_event(event, 'up')
        self.set_table_specified_state(self.on_cur_select_table, ((self.last_click_select_start[0], self.last_click_select_end[0]), (self.last_click_select_start[1], self.last_click_select_end[1])), TableEditor.SELECTED)

    
    def on_move(self, event):
        self.canvas.set_table_specified_color(((self.last_click_select_start[0], self.last_click_select_end[0]), (self.last_click_select_start[1], self.last_click_select_end[1])), TableEditor.WHITE_FORMAT)
        pos_end = self.canvas.screen_coord_to_led_coord((event.x, event.y))
        print('cur led_coord', pos_end)
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
                self.canvas.canvas.itemconfig(self.canvas.arr2[i][j], TableEditor.SELECT_COLOR, **('fill',))
            
        

    
    def screen_mouse_event(self, event, state = ('down',)):
        if state == 'down':
            pos = self.canvas.screen_coord_to_led_coord((event.x, event.y))
            state = TableEditor.TREAD
            print('click down', pos[0], pos[1], state)
        else:
            pos = self.canvas.screen_coord_to_led_coord((event.x, event.y))
            state = TableEditor.NO_TREAD
            print('click up', pos[0], pos[1], state)
        row = pos[0]
        col = pos[1]
        self.led_coors_click = ((row, col), state)

    
    def screen_mouse_event_wall_table(self, event, state = ('down',)):
        if state == 'down':
            pos = self.canvas.screen_coord_to_led_coord((event.x, event.y))
            state = TableEditor.TREAD
            print('click down', pos[0], pos[1], state)
        else:
            pos = self.canvas.screen_coord_to_led_coord((event.x, event.y))
            state = TableEditor.NO_TREAD
            print('click up', pos[0], pos[1], state)
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

    
    def add_right_button_command(self, label, command = ('', None)):
        self.menu.add_command(label, command, **('label', 'command'))

    
    def menupop(self, event, menu):
        led_coor = self.canvas.screen_coord_to_led_coord((event.x, event.y))
        if self.on_cur_select_table[led_coor[0]][led_coor[1]] == TableEditor.SELECTED:
            menu.post(event.x_root, event.y_root)

    
    def cal_wall_pos_anther(self, high, width):
        if self.obj_parent.game_setting.screen:
            m = high - 4
            n = width - 4
            row_wall = 2
            col_wall = 5
            row = m
            col = n
            tmp_arr = []
            light_num = 0
            for j in range(col):
                if (j + 1) % 3 == 0:
                    light_num += 1
                    tmp_arr.append([
                        1,
                        j + 2])
            tmp = col
            for i in range(row - 1):
                if (i + tmp + 1) % 3 == 0:
                    light_num += 1
                    tmp_arr.append([
                        i + 3,
                        width - 2])
            tmp = tmp + row - 1
            for j in range(col - 1):
                if (j + tmp + 1) % 3 == 0:
                    light_num += 1
                    tmp_arr.append([
                        high - 2,
                        col - j])
            tmp = tmp + col - 1
            for i in range(row - 1):
                if (i + tmp + 1) % 3 == 0:
                    light_num += 1
                    tmp_arr.append([
                        (row - 2 - i) + 2,
                        1])
            i = 0
            for coors in tmp_arr:
                i = i + 1
                self.canvas.write_text_in_table(coors, str(i))
            

    
    def get_wall_light_table(self):
        return self.wall_light_table

    
    def cal_wall_pos(self, high, width):
        self.wall_light_table = []
        self.wall_screen_table = []
        self.parent.floor_light_row_start = 0
        self.parent.floor_light_col_start = 0
        m = high
        n = width
        if self.obj_parent.game_setting.screen:
            m = high - 4
            n = width - 4
            row_wall = 2
            col_wall = 5
            self.parent.floor_light_row_start = 2
            self.parent.floor_light_col_start = 2
            light_total_num = int((2 * m + 2 * n - 4) / 3)
            for i in range(light_total_num):
                self.wall_light_table.append((row_wall - 1, col_wall - 1))
                if row_wall == 2:
                    col_wall = col_wall + 3
                    if col_wall > 2 + n:
                        col_wall = n + 3
                        row_wall = (3 - n % 3) + 3
                        self.wall_light_table.append((row_wall - 1, col_wall - 1))
                if col_wall == n + 3:
                    row_wall = row_wall + 3
                    if row_wall > 2 + m:
                        row_wall = m + 3
                        col_wall = 2 + n - 3 - (n + m - 1) % 3
                        self.wall_light_table.append((row_wall - 1, col_wall - 1))
                if row_wall == m + 3:
                    col_wall = col_wall - 3
                    if col_wall < 3:
                        col_wall = 2
                        row_wall = 2 + m - 3 - (2 * n + m - 2) % 3
                        self.wall_light_table.append((row_wall - 1, col_wall - 1))
                if col_wall == 2:
                    row_wall = row_wall - 3
            tmp_w = 2
            row_wall = 1
            col_wall = 5
            for i in range(light_total_num):
                self.wall_screen_table.append((row_wall - 1, col_wall - 1))
                if row_wall == 1:
                    col_wall = col_wall + 3
                    if col_wall > 2 + n:
                        col_wall = n + 4
                        row_wall = (3 - n % 3) + 3
                        self.wall_screen_table.append((row_wall - 1, col_wall - 1))
                if col_wall == n + 4:
                    row_wall = row_wall + 3
                    if row_wall > 2 + m:
                        row_wall = m + 4
                        col_wall = 2 + n - 3 - (n + m - 1) % 3
                        self.wall_screen_table.append((row_wall - 1, col_wall - 1))
                if row_wall == m + 4:
                    col_wall = col_wall - 3
                    if col_wall < 3:
                        col_wall = 1
                        row_wall = 2 + m - 3 - (2 * n + m - 2) % 3
                        self.wall_screen_table.append((row_wall - 1, col_wall - 1))
                if col_wall == 1:
                    row_wall = row_wall - 3
        if self.obj_parent.game_setting.wall_light:
            m = high - 2
            n = width - 2
            row_wall = 1
            col_wall = 4
            self.parent.floor_light_row_start = 1
            self.parent.floor_light_col_start = 1
            light_total_num = int((2 * m + 2 * n - 4) / 3)
            for i in range(light_total_num):
                self.wall_light_table.append((row_wall - 1, col_wall - 1))
                if row_wall == 1:
                    col_wall = col_wall + 3
                    if col_wall > 1 + n:
                        col_wall = n + 2
                        row_wall = (3 - n % 3) + 2
                        self.wall_light_table.append((row_wall - 1, col_wall - 1))
                if col_wall == n + 2:
                    row_wall = row_wall + 3
                    if row_wall > 1 + m:
                        row_wall = m + 2
                        col_wall = 1 + n - 3 - (n + m - 1) % 3
                        self.wall_light_table.append((row_wall - 1, col_wall - 1))
                if row_wall == m + 2:
                    col_wall = col_wall - 3
                    if col_wall < 2:
                        col_wall = 1
                        row_wall = 1 + m - 3 - (2 * n + m - 2) % 3
                        self.wall_light_table.append((row_wall - 1, col_wall - 1))
                if col_wall == 1:
                    row_wall = row_wall - 3
        self.canvas.create_canvas_text_arr()
        i = 0
        for coors in self.wall_screen_table:
            i = i + 1
            self.canvas.write_rect_color_in_table(coors, Color.WHITE_GREEN_FORMAT, **('color',))
        
        i = 0
        for coors in self.wall_light_table:
            i = i + 1
            self.canvas.write_text_in_table(coors, '灯' + str(i))
        
        floor_start = self.canvas.led_coord_to_screen_coord((self.parent.floor_light_row_start, self.parent.floor_light_col_start))
        floor_end = self.canvas.led_coord_to_screen_coord((self.parent.floor_light_row_start + m, self.parent.floor_light_col_start + n))
        tmp = self.canvas.canvas.create_rectangle(floor_start[1], floor_start[0], floor_end[1], floor_end[0], 'k', 'black', **('tags', 'outline'))

    
    def get_led_table(self):
        for i in range(len(self.led_table)):
            for j in range(len(self.led_table[0])):
                str_t = self.led_table[i][j]
                tuple_tmp = (int(str_t[1:3], 16, **('base',)), int(str_t[3:5], 16, **('base',)), int(str_t[5:7], 16, **('base',)))
                self.tmp_led_table[i][j] = tuple_tmp
            
        
        return self.tmp_led_table

    
    def get_state_table(self):
        return self.table_state

    
    def __init__(self, root, obj_parent, ui_table_row, ui_table_col, head_start = (0,)):
        high = ui_table_row
        width = ui_table_col
        self.led_coors_click = ((0, 0), 0)
        self.led_coors_click_wall = ((0, 0), 0)
        self.table_state = (lambda _iter_ = None: [ [
True] * width for _ in .0 ])(range(high))
        self.led_table = (lambda _iter_ = None: [ [
gui_color.GRAY] * width for _ in .0 ])(range(high))
        self.led_table_text = (lambda _iter_ = None: [ [
''] * width for _ in .0 ])(range(high))
        self.on_cur_select_table = (lambda _iter_ = None: [ [
bool] * width for _ in .0 ])(range(high))
        self.obj_parent = obj_parent
        self.parent = self.obj_parent
        fm_her1 = ttk.Frame(root)
        fm_her1.pack()
        led_title_none = canvas_led.CanvasLed(fm_her1, 1, 1, 22, **('side',))
        led_title_none.canvas.pack('left', **('side',))
        led_title_her = canvas_led.CanvasLed(fm_her1, 1, width, 22, **('side',))
        led_title_her.canvas.pack('left', **('side',))
        led_title_her.write_serial_num_in_rectangle(0, head_start, **('direct', 'start'))
        fm_her2 = ttk.Frame(root)
        fm_her2.pack()
        led_title_ver = canvas_led.CanvasLed(fm_her2, high, 1, 22, **('side',))
        led_title_ver.canvas.pack('left', **('side',))
        led_title_ver.write_serial_num_in_rectangle(1, head_start, **('direct', 'start'))
        self.canvas = None
        led_canvas = canvas_led.CanvasLed(fm_her2, high, width, 22, **('side',))
        canvas = led_canvas.canvas
        canvas.pack('left', 'both', **('side', 'fill'))
        canvas.bind('<ButtonPress-1>', self.start_move)
        canvas.bind('<ButtonRelease-1>', self.stop_move)
        canvas.bind('<B1-Motion>', self.on_move)
        canvas.bind('<Control-ButtonPress-1>', self.start_move_ctrl)
        None(None, (lambda event = None: self.menupop(event, self.menu)))
        self.canvas = led_canvas
        self.menu = Menu(canvas)
        self.canvas.create_canvas_text_arr()
        self.canvas.canvas.create_rectangle(0, 0, 0, 0, 'L', 'black', **('tags', 'outline'))


