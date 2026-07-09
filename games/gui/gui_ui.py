# Source Generated with Decompyle++
# File: gui_ui.pyc (Python 3.7)

import decimal
import time
from tkinter import Toplevel, Canvas, ttk, Frame
from PIL import ImageTk, Image
from loguru import logger
from gui.language import language
from gui2.gui_led_table_editor import LedTable
from model.setting import Setting, Color
from util.image_process import ImageProcess

class GuiUI:
    
    def color_int_arr2hex_str(self, color_int_arr):
        str_hex = '#' + '{:02x}{:02x}{:02x}'.format(color_int_arr[0], color_int_arr[1], color_int_arr[2])
        return str_hex

    
    def color_hex_str2int_arr(self, str_color):
        return (int(str_color[1:3], 16), int(str_color[3:5], 16), int(str_color[5:7], 16))

    
    def half_up(self, data):
        return int(decimal.Decimal(data).quantize(decimal.Decimal('0'), decimal.ROUND_HALF_UP, **('rounding',)))

    
    def ui_time_sleep(self, sec):
        idx = 0
        while idx < sec:
            time.sleep(0.2)
            self.root.update()
            idx += 0.2

    
    def closeUI(self):
        logger.info('UI close')
        self.root.update()

    
    def button_back(self):
        logger.info('Game UI button back click')
        self.parent.customized_function()

    
    def update_game_name_ui(self, game_name):
        self.canvas.itemconfig('tag_game_name', game_name, **('text',))
        self.root.update()

    
    def ui_game_corporation(self, row, col, wall_light_arr_len):
        root = self.root
        self.full_screen = True
        root.attributes('-fullscreen', Setting.FULL_SCREEN)
        root.attributes('-topmost', 'true')
        (scnWidth, scnHeight) = root.maxsize()
        canvas = Canvas(root, scnWidth, scnHeight, 'black', **('width', 'height', 'bg'))
        self.canvas = canvas
        image = Image.open('./photo/game_running.jpg')
        image = image.resize((int(scnWidth), int(scnHeight)), Image.ANTIALIAS)
        self.bg_image_file = ImageTk.PhotoImage(image)
        canvas.create_image(int(scnWidth / 2), int(scnHeight / 2), self.bg_image_file, **('image',))
        self.list_image = [
            None] * 5
        image = Image.open('./photo/white_heart.png')
        image = image.resize((int(scnWidth / 13), int(scnHeight / 8)), Image.ANTIALIAS)
        self.image_file = ImageTk.PhotoImage(image)
        for i in range(5):
            self.list_image[i] = canvas.create_image(int(scnWidth / 4) + image.width / 2 + i * int(scnWidth / 9.5), 0.136111 * scnHeight, self.image_file, **('image',))
        
        canvas.pack()
        root = self.root
        canvas = self.canvas
        (scnWidth, scnHeight) = root.maxsize()
        divide_width = 6
        divide_height = 8
        color = '#CCFFFF'
        text_scode = canvas.create_text(0.273438 * scnWidth, 0.651852 * scnHeight, language.SCORE, ('STKaiti', int(0.015625 * scnWidth), 'bold'), 'white', **('text', 'font', 'fill'))
        self.text_scode_value = canvas.create_text(0.527083 * scnWidth, 0.646296 * scnHeight, '0', ('STKaiti', int(0.15625 * scnWidth), 'bold'), 'black', **('text', 'font', 'fill'))
        canvas.create_text(0.433854 * scnWidth, 0.361111 * scnHeight, language.COUNT_DOWN, ('STKaiti', int(0.0104167 * scnWidth), 'bold'), 'black', **('text', 'font', 'fill'))
        self.text_time_value = canvas.create_text(0.511458 * scnWidth, 0.361111 * scnHeight, '0', ('STKaiti', int(0.03125 * scnWidth), 'bold'), 'black', **('text', 'font', 'fill'))
        canvas.create_text(0.50625 * scnWidth, 0.898148 * scnHeight, '', ('STKaiti', int(0.03125 * scnWidth), 'bold'), 'white', 'tag_game_name', **('text', 'font', 'fill', 'tag'))
        x1 = scnWidth - 0.0677083 * scnWidth
        x2 = x1 + int(0.0625 * scnWidth)
        y1 = scnHeight - 0.0925926 * scnHeight
        y2 = y1 + int(0.037037 * scnHeight)
        a = ttk.Style()
        a.configure('my.TButton', ('STKaiti', int(0.015625 * scnWidth), 'bold'), 'gray', **('font', 'foreground'))
        ttk.Button(canvas, language.BACK, 'my.TButton', 6, self.button_back, **('text', 'style', 'width', 'command')).place(0.9, 0.9, **('relx', 'rely'))
        table_frame = Frame(root)
        self.led_table = LedTable(table_frame, wall_light_arr_len, row, col)
        size = self.led_table.get_canvas_table_size()
        table_frame.place(5 / scnWidth, 1 - (size[1] + 100) / scnHeight, **('relx', 'rely'))
        root.update()
        root.state('zoomed')
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        print(curWidth, curHeight)
        (scnWidth, scnHeight) = root.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol('WM_DELETE_WINDOW', self.parent.customized_function)
        root.iconbitmap('./photo/ledplay.ico')

    
    def ui_editor_game2(self, row, col, gun_nums):
        root = self.root
        img_pro = self.img_process
        player_nums = self.parent.player_nums
        list_player_name = self.parent.list_player_name
        list_score = self.parent.color_scode
        list_bullet = self.parent.color_bullet
        list_color = self.parent.color_array
        root.attributes('-fullscreen', Setting.FULL_SCREEN)
        root.attributes('-topmost', 'true')
        (scnWidth, scnHeight) = root.maxsize()
        canvas = Canvas(root, scnWidth, scnHeight, 'black', 0, 0, **('width', 'height', 'bg', 'borderwidth', 'highlightthickness'))
        canvas.pack()
        self.bg_image_file = img_pro.generate('./photo/laser/laser_running_bgm.png', scnWidth, scnHeight)
        canvas.create_image(int(scnWidth / 2), int(scnHeight / 2), self.bg_image_file, **('image',))
        color_hig_start = scnHeight / 11
        color_hig_start2 = scnHeight / 13.4
        color = 'white'
        canvas.create_text(0.640625 * scnWidth, color_hig_start, language.COUNT_DOWN + language.COLON, ('STKaiti', int(0.00885417 * scnWidth)), color, **('text', 'font', 'fill'))
        self.text_time_value = canvas.create_text(0.729167 * scnWidth, color_hig_start2, '0', 'clock', ('STKaiti', int(0.03125 * scnWidth), 'bold'), color, **('text', 'tags', 'font', 'fill'))
        self.list_image = [
            None] * 5
        self.image_file = self.img_process.generate('./photo/white_heart.png', int(scnWidth / 13), int(scnHeight / 8))
        for i in range(5):
            self.list_image[i] = canvas.create_image(int(scnWidth / 4) + self.image_file.width() / 2 + i * int(scnWidth / 9.5), 0.277778 * scnHeight, self.image_file, **('image',))
        
        canvas.pack()
        width_start_title = scnWidth / 10
        height_start_title = scnHeight / 2
        row_size = scnHeight / 5
        width_span_content = scnWidth * 4 / 5 / player_nums
        width_start_content = scnWidth * 0.1 + scnWidth * 0.8 / (player_nums * 2)
        canvas.create_text(width_start_title, height_start_title, language.PLAYER, ('STKaiti', int(0.00520833 * scnWidth)), color, **('text', 'font', 'fill'))
        canvas.create_text(width_start_title, height_start_title + row_size, language.SCORE, ('STKaiti', int(0.00520833 * scnWidth)), color, **('text', 'font', 'fill'))
        size = 60 + (6 - player_nums) * 20
        if size < 60:
            size = 60
        for i in range(player_nums):
            canvas.create_text(width_start_content + width_span_content * i, height_start_title, list_player_name[i], ('STKaiti', int((size * 1 / 3 / 1920) * scnWidth)), self.color_int_arr2hex_str(list_color[i]), **('text', 'font', 'fill'))
            canvas.create_text(width_start_content + width_span_content * i, height_start_title + row_size, list_score[i], ('STKaiti', int((size / 1920) * scnWidth)), self.color_int_arr2hex_str(list_color[i]), 'score' + str(i + 1), **('text', 'font', 'fill', 'tags'))
        
        canvas.create_text(0.270833 * scnWidth, 0.0740741 * scnHeight, '', ('STKaiti', int(0.015625 * scnWidth), 'bold'), 'white', 'tag_game_name', **('text', 'font', 'fill', 'tag'))
        self.canvas = canvas
        a = ttk.Style()
        a.configure('my.TButton', ('STKaiti', int(0.015625 * scnWidth), 'bold'), 'gray', **('font', 'foreground'))
        ttk.Button(canvas, language.BACK, 'my.TButton', 6, self.button_back, **('text', 'style', 'width', 'command')).place(0.9, 0.93, **('relx', 'rely'))
        table_frame = Frame(root)
        self.led_table = LedTable(table_frame, gun_nums, row, col)
        size = self.led_table.get_canvas_table_size()
        table_frame.place(5 / scnWidth, 1 - (size[1] + 100) / scnHeight, **('relx', 'rely'))
        root.update()
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        print(curWidth, curHeight)
        (scnWidth, scnHeight) = root.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol('WM_DELETE_WINDOW', self.parent.customized_function)
        root.iconbitmap('./photo/ledplay.ico')

    
    def ui_game_battle(self, row, col, wall_light_arr_len):
        root = self.root
        self.full_screen = True
        root.attributes('-fullscreen', Setting.FULL_SCREEN)
        root.attributes('-topmost', 'true')
        (scnWidth, scnHeight) = root.maxsize()
        canvas = Canvas(root, scnWidth, scnHeight, 'black', **('width', 'height', 'bg'))
        self.canvas = canvas
        None(None, (lambda event = None: self.screen_mouse_event(event, root)))
        image = Image.open('./photo/caise.png')
        image = image.resize((int(scnWidth), int(scnHeight)), Image.ANTIALIAS)
        self.bg_image_file = ImageTk.PhotoImage(image)
        canvas.create_image(int(scnWidth / 2), int(scnHeight / 2), self.bg_image_file, **('image',))
        self.left_list_image = [
            None] * 5
        self.right_list_image = [
            None] * 5
        red_heart = './photo/white_heart.png'
        img_process = ImageProcess()
        self.image_red_heart = img_process.generate(red_heart, int(scnWidth / 12), int(scnHeight / 7))
        yellow_star = './photo/game_type/start.JPEG'
        self.image_yellow_star = img_process.generate(yellow_star, int(scnWidth / 11.8), int(scnHeight / 6.8))
        width_start = 0
        height_start = int(scnHeight / 6)
        color = '#CCFFFF'
        canvas.create_text(scnWidth / 4, scnHeight / 2.5, '', ('STKaiti', int(0.078125 * scnWidth)), color, 'text_game_result_left', **('text', 'font', 'fill', 'tags'))
        for i in range(1, 6, 1):
            self.left_list_image[i - 1] = canvas.create_image(width_start + i * (scnWidth / 10) - scnWidth / 20, height_start, self.image_red_heart, **('image',))
        
        width_start = int(scnWidth / 2)
        canvas.create_text(scnWidth * 3 / 4, scnHeight / 2.5, '', ('STKaiti', int(0.078125 * scnWidth)), color, 'text_game_result_right', **('text', 'font', 'fill', 'tags'))
        for i in range(1, 6, 1):
            self.right_list_image[i - 1] = canvas.create_image(width_start + i * (scnWidth / 9.9) - scnWidth / 19.8, height_start, self.image_yellow_star, **('image',))
        
        canvas.pack()
        root = self.root
        canvas = self.canvas
        (scnWidth, scnHeight) = root.maxsize()
        divide_width = 6
        divide_height = 8
        first_positon_x = 2 * scnWidth / divide_width
        two_position_x = 4 * scnWidth / divide_width
        three_position_y = scnHeight - scnHeight / divide_height
        three_position_x = scnWidth - scnWidth / divide_width
        two_position_y = 4 * scnHeight / divide_height
        lable_start_position_width = scnWidth / 3 / 2
        lable_start_position_height = scnHeight - scnHeight / 10
        lable_width = scnWidth / 3
        position_index = 0
        value_start_position_width = lable_start_position_width
        value_start_position_height = 0.65 * scnHeight
        value_width = lable_width
        canvas.create_text(lable_start_position_width + position_index * lable_width, lable_start_position_height, language.SCORE, ('STKaiti', int(0.0260417 * scnWidth)), color, **('text', 'font', 'fill'))
        self.text_scode_value_left = canvas.create_text(value_start_position_width + position_index * value_width, value_start_position_height, '0', ('STKaiti', int(0.078125 * scnWidth)), 'white', **('text', 'font', 'fill'))
        position_index += 1
        canvas.create_text(lable_start_position_width + position_index * lable_width, lable_start_position_height, language.TIME, ('STKaiti', int(0.0260417 * scnWidth)), color, **('text', 'font', 'fill'))
        self.text_time_value = canvas.create_text(value_start_position_width + position_index * value_width, value_start_position_height, '0', ('STKaiti', int(0.0520833 * scnWidth)), 'white', **('text', 'font', 'fill'))
        position_index += 1
        canvas.create_text(lable_start_position_width + position_index * lable_width, lable_start_position_height, language.SCORE, ('STKaiti', int(0.0260417 * scnWidth)), color, **('text', 'font', 'fill'))
        self.text_scode_value_right = canvas.create_text(value_start_position_width + position_index * value_width, value_start_position_height, '0', ('STKaiti', int(0.078125 * scnWidth)), 'white', **('text', 'font', 'fill'))
        a = ttk.Style()
        a.configure('my.TButton', ('STKaiti', int(0.015625 * scnWidth), 'bold'), 'gray', **('font', 'foreground'))
        ttk.Button(canvas, language.BACK, 'my.TButton', 6, self.button_back, **('text', 'style', 'width', 'command')).place(0.9, 0.93, **('relx', 'rely'))
        table_frame = Frame(root)
        self.led_table = LedTable(table_frame, wall_light_arr_len, row, col)
        size = self.led_table.get_canvas_table_size()
        table_frame.place(5 / scnWidth, 1 - (size[1] + 100) / scnHeight, **('relx', 'rely'))
        root.update()
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        print(curWidth, curHeight)
        (scnWidth, scnHeight) = root.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol('WM_DELETE_WINDOW', self.parent.customized_function)
        root.iconbitmap('./photo/ledplay.ico')

    
    def reset_life_value_ui(self, side = (0,)):
        if self.mode == 0:
            for i in range(4, 0, -1):
                self.canvas.itemconfig(self.list_image[i], 'normal', **('state',))
            
        elif self.mode == 1:
            for i in range(4, -1, -1):
                if side == 0:
                    self.canvas.itemconfig(self.left_list_image[i], 'normal', **('state',))
                    continue
                self.canvas.itemconfig(self.right_list_image[i], 'normal', **('state',))
            
        elif self.mode == 2:
            for i in range(4, 0, -1):
                self.canvas.itemconfig(self.list_image[i], 'normal', **('state',))
            

    
    def update_life_value_ui_1(self, life_value):
        end_idx = self.half_up(5 * life_value / self.blood_total)
        if end_idx < 1:
            end_idx = 1
        for i in range(4, end_idx - 1, -1):
            if self.list_image[i] is not None:
                self.canvas.itemconfig(self.list_image[i], 'hidden', **('state',))

    
    def update_data_ui(self, scode, life_vale, time = (0,)):
        if scode >= 0:
            scode_format = '{:0>4}'.format(scode)
        else:
            scode_format = '-{:0>3}'.format(abs(scode))
        if time < 0:
            time = 0
        time_format = '{:0>2}:{:0>2}'.format(int(time / 60), int(time % 60))
        self.canvas.itemconfig(self.text_scode_value, scode_format, **('text',))
        self.canvas.itemconfig(self.text_time_value, time_format, **('text',))
        self.update_life_value_ui_1(life_vale)
        if life_vale < life_vale or life_vale <= 0:
            pass
        else:
            -2
        self.reset_life_value_ui()
        self.root.update()

    
    def update_life_value_ui_2(self, game_record):
        game1_blood = game_record.game_blood_left
        game2_blood = game_record.game_blood_right
        if game1_blood < game1_blood or game1_blood <= 0:
            pass
        else:
            -2
        self.reset_life_value_ui(0)
        if game2_blood < game2_blood or game2_blood <= 0:
            pass
        else:
            -2
        self.reset_life_value_ui(1)
        end_idx = self.half_up(5 * game1_blood / self.blood_total)
        for i in range(4, end_idx - 1, -1):
            if self.left_list_image[i] is not None:
                self.canvas.itemconfig(self.left_list_image[i], 'hidden', **('state',))
        end_idx = self.half_up(5 * game2_blood / self.blood_total)
        for i in range(4, end_idx - 1, -1):
            if self.right_list_image[i] is not None:
                self.canvas.itemconfig(self.right_list_image[i], 'hidden', **('state',))

    
    def update_editor_game1(self, game_record):
        game1_scode = game_record.game_scode_left
        game2_scode = game_record.game_scode_right
        time_left = game_record.game_time_left
        if game1_scode >= 0:
            left_scode_format = '{:0>4}'.format(game1_scode)
        else:
            left_scode_format = '-{:0>3}'.format(abs(game1_scode))
        if game2_scode >= 0:
            right_scode_format = '{:0>4}'.format(game2_scode)
        else:
            right_scode_format = '-{:0>3}'.format(abs(game2_scode))
        if time_left < 0:
            time_left = 0
        time_format = '{:0>2}:{:0>2}'.format(int(time_left / 60), int(time_left % 60))
        self.canvas.itemconfig(self.text_scode_value_left, left_scode_format, **('text',))
        self.canvas.itemconfig(self.text_scode_value_right, right_scode_format, **('text',))
        self.canvas.itemconfig(self.text_time_value, time_format, **('text',))
        self.update_life_value_ui_2(game_record)
        self.root.update()

    
    def update_editor_game2(self, game_record):
        game2_scode = game_record.game_scode_right
        time_left = game_record.game_time_left
        list_score = game_record.game_info[0]
        life_vale = game_record.game_blood
        list_format_score = []
        for score in list_score:
            if score >= 0:
                score = '{:0>4}'.format(score)
            else:
                score = '-{:0>3}'.format(abs(score))
            list_format_score.append(score)
        
        list_format_bullet = []
        if time_left < 0:
            time_left = 0
        time_format = '{:0>2}:{:0>2}'.format(int(time_left / 60), int(time_left % 60))
        self.canvas.itemconfig('clock', time_format, **('text',))
        for i in range(len(list_score)):
            self.canvas.itemconfig('score' + str(i + 1), list_format_score[i], **('text',))
        
        self.update_life_value_ui_1(life_vale)
        if life_vale <= 0:
            self.reset_life_value_ui()
        self.root.update()

    
    def update_ui(self, game_record = (None,)):
        mode = self.mode
        self.led_table.draw_color(self.wall_line)
        if game_record:
            if mode == 0:
                if game_record.game_blood <= 0:
                    game_record.game_result = 0
                self.update_data_ui(game_record.game_scode, game_record.game_blood, game_record.game_time_left)
            elif mode == 1:
                self.update_editor_game1(game_record)
            elif mode == 2:
                if game_record.game_blood <= 0:
                    game_record.game_result = 0
                self.update_editor_game2(game_record)

    
    def reset_result_text(self):
        self.canvas.itemconfig('text_game_result_left', '', **('text',))
        self.canvas.itemconfig('text_game_result_right', '', **('text',))
        self.reset_life_value_ui(0)
        self.reset_life_value_ui(1)

    
    def update_result_text(self, score1, score2):
        if score1 < score2:
            side = 1
        elif score1 > score2:
            side = 0
        else:
            side = -1
        if side == 0:
            rig_color = Color.RED_FORMAT
            lft_color = Color.GREEN_FORMAT
            rig_text = language.LOSE
            lft_text = language.WIN
        elif side == 1:
            rig_color = Color.GREEN_FORMAT
            lft_color = Color.RED_FORMAT
            rig_text = language.WIN
            lft_text = language.LOSE
        else:
            rig_color = Color.GREEN_FORMAT
            lft_color = Color.GREEN_FORMAT
            rig_text = language.TIE
            lft_text = language.TIE
        self.canvas.itemconfig('text_game_result_left', lft_text, lft_color, **('text', 'fill'))
        self.canvas.itemconfig('text_game_result_right', rig_text, rig_color, **('text', 'fill'))
        print('update_result_text')

    
    def __init__(self, parent, blood_total, led_row, led_col, wall_light_arr_len, wall_line, mode = (0,)):
        self.root = Toplevel()
        self.img_process = ImageProcess()
        self.blood_total = blood_total
        self.wall_line = wall_line
        self.mode = mode
        self.parent = parent
        parent.game_record_rt.running_to_flag = 1
        if mode == 0:
            self.ui_game_corporation(led_row, led_col, wall_light_arr_len)
        elif mode == 1:
            self.ui_game_battle(led_row, led_col, wall_light_arr_len)
        elif mode == 2:
            self.ui_editor_game2(led_row, led_col, wall_light_arr_len)

    
    def ui_loop(self):
        self.root.mainloop()


