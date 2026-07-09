# Source Generated with Decompyle++
# File: gui_game_level_select.pyc (Python 3.7)

import random
import sys
import time
import tkinter
import traceback
from threading import Thread
from tkinter import ttk
import loguru
from PIL import ImageTk, Image
from gui.gui_countdown import GuiCountDown
from gui.gui_game_ranking_canvas import GameRankingCanvas
from gui.gui_game_result import GameResult
from gui.gui_player_login import PlayerLogin
from gui.language import language
from model.setting import Setting
from tourist_record.tourist_record_main import TouristRecord
from ui_design.button_canvas import Button_Canvas
from ui_design.entry_canvas import Entry_Canvas
from util.image_process import ImageProcess
from functools import partial

class GameLevelSelect:
    
    def update_level_btn1(self):
        color = '#66ffff'
        self.list_btn_level_slt[0].image_path = self.list_game_level_btn_img_bgm_path[self.cur_level - 1]
        self.list_btn_level_slt[0].focus_on(color)

    
    def on_screen_click_level_slt(self, event, list_button):
        color = '#66ffff'
        for i, button in enumerate(list_button):
            if button.click(event):
                button.focus_on(color, False, **('voice',))
                self.cur_level = i + 1
                continue
            button.focus_off()
        
        self.update_level_btn1()

    
    def on_screen_click_level_btn(self, event, list_button):
        color = '#66ffff'
        for button in list_button:
            if button.click(event):
                button.focus_on(color)
                continue
            button.focus_off()
        

    
    def on_screen_click_back_next_btn(self, event, list_button):
        color = '#66ffff'
        for button in list_button:
            if button.focus or button.click(event):
                button.focus_on(color)
                continue
            button.focus_off()
        

    
    def on_screen_keypress(self, event, list_button):
        for item in list_button:
            if item.focus:
                str_char = '{0}'.format(event.char)
                item.input(str_char)

    
    def get_list_size_rate(self, cur_level):
        select_size_rate = 1.15
        unselect_size_rate = (3 - select_size_rate) / 2
        list_size_rate = [
            1,
            1,
            1]
        for idx, rate in enumerate(list_size_rate):
            if idx == cur_level - 1:
                list_size_rate[idx] *= select_size_rate
                continue
            list_size_rate[idx] *= unselect_size_rate
        
        return list_size_rate

    
    def create_game_level_slt(self, frame, list_game_type):
        (scnWidth, scnHeight) = self.root_size
        img_process = self.img_process
        self.list_canvas_button = []
        self.list_list_btn.append(self.list_canvas_button)
        canvas = tkinter.Canvas(frame, scnWidth, scnHeight / 4, 0, 0, **('width', 'height', 'borderwidth', 'highlightthickness'))
        canvas.pack('center', **('anchor',))
        if self.editable:
            None(None, (lambda event = None: self.on_screen_click_level_slt(event, self.list_canvas_button)))
        path_img_bgm1 = './photo/game_main.png'
        region = (0, 0, scnWidth, scnHeight / 4)
        time_bft = time.time()
        self.image_file_game_list = img_process.crop_img(path_img_bgm1, scnWidth, scnHeight, region)
        canvas.create_image(0, 0, 'nw', self.image_file_game_list, 'background', **('anchor', 'image', 'tag'))
        print(time.time() - time_bft)
        list_game_type_img_bgm_path = [
            './photo/game_type/simple.jpeg',
            './photo/game_type/normal.jpeg',
            './photo/game_type/difficult.jpeg']
        main_canvas = canvas
        type_width = scnWidth / 6
        game_type_width_mid_list = [
            0.25 * scnWidth,
            0.5 * scnWidth,
            0.75 * scnWidth]
        type_height = scnHeight / 7.2
        game_type_height_mid = (0.5 * scnHeight / 8) * 2.5
        for i in range(len(list_game_type)):
            y1 = game_type_height_mid - type_height / 2
            y2 = game_type_height_mid + type_height / 2
            x1 = game_type_width_mid_list[i] - type_width / 2
            x2 = game_type_width_mid_list[i] + type_width / 2
            bt_game_type = Button_Canvas(main_canvas, x1, y1, x2, y2, list_game_type[i], 25, '#1e90ff', '#3399ff', 'game_type', None, list_game_type_img_bgm_path[i], 1.2, 0.933333, 'sw', **('d_outline', 'd_fill', 'btn_type', 'image', 'image_path', 'zone_out', 'zone_in', 'anchor'))
            if i == self.cur_level - 1:
                bt_game_type.focus_on('#66ffff', False, **('voice',))
            self.list_canvas_button.append(bt_game_type)
        

    
    def create_game_level_fix(self, frame, cur_level):
        (scnWidth, scnHeight) = self.root_size
        img_process = self.img_process
        canvas = tkinter.Canvas(frame, scnWidth, scnHeight / 4, 0, 0, **('width', 'height', 'borderwidth', 'highlightthickness'))
        canvas.pack('center', **('anchor',))
        path_img_bgm1 = './photo/game_main.png'
        region = (0, 0, scnWidth, scnHeight / 4)
        self.img_level_fix_bg = img_process.crop_img(path_img_bgm1, scnWidth, scnHeight, region)
        canvas.create_image(0, 0, 'nw', self.image_file_game_list, 'background', **('anchor', 'image', 'tag'))
        self.img_level_fix = []
        img_level_fix = self.img_level_fix
        path_game_level_fix = './photo/game_type/start.jpeg'
        type_width = scnWidth / 10
        type_height = scnWidth / 11.6
        game_type_width_mid_list = [
            0.25 * scnWidth,
            0.5 * scnWidth,
            0.75 * scnWidth]
        game_type_height_mid = (0.5 * scnHeight / 8) * 2.5
        for i in range(cur_level):
            img_level_fix.append(img_process.generate(path_game_level_fix, round(type_width), round(type_height)))
            canvas.create_image(game_type_width_mid_list[i], game_type_height_mid, 'center', img_level_fix[i], 'background', **('anchor', 'image', 'tag'))
        

    
    def command_level_btn_slt(self):
        self.fm_picture_2.grid_forget()
        self.fm_picture_1.grid(0, 0, **('row', 'column'))

    
    def command_level_btn_fix(self):
        self.fm_picture_1.grid_forget()
        self.fm_picture_2.grid(0, 0, **('row', 'column'))

    
    def create_level_select_button(self, frame, cur_level = (1,)):
        list_button_name = [
            language.LEVAL,
            language.GAME_LIFE,
            language.GAME_TIME,
            language.AGILE]
        self.list_btn_level_slt = []
        self.list_list_btn.append(self.list_btn_level_slt)
        path_button_frame = './photo/new/introduce_rect.PNG'
        list_game_type_img_bgm_path = self.list_game_level_btn_img_bgm_path
        (scnWidth, scnHeight) = self.root_size
        img_process = self.img_process
        canvas_height = scnHeight * 4 / 20
        canvas = tkinter.Canvas(frame, scnWidth, canvas_height, 0, 0, **('width', 'height', 'borderwidth', 'highlightthickness'))
        canvas.pack('center', **('anchor',))
        canvas.focus_set()
        None(None, (lambda event = None: self.on_screen_click_level_btn(event, self.list_btn_level_slt)))
        self.list_input_btn = []
        None(None, (lambda event = None: self.on_screen_keypress(event, self.list_input_btn)))
        path_img_bgm1 = './photo/game_main.png'
        region = (0, scnHeight / 4, scnWidth, scnHeight / 4 + canvas_height)
        self.img_level_slt_btn_bg = img_process.crop_img(path_img_bgm1, scnWidth, scnHeight, region)
        canvas.create_image(0, 0, 'nw', self.img_level_slt_btn_bg, 'background', **('anchor', 'image', 'tag'))
        type_width = scnWidth / 13.5
        game_type_width_mid_list = [
            0.25 * scnWidth,
            0.416667 * scnWidth,
            0.583333 * scnWidth,
            0.75 * scnWidth]
        type_height = scnHeight / 20
        game_type_height_mid = (0.5 * scnHeight / 8) * 1.8
        btn_level_select = partial(self.command_level_btn_slt)
        btn_level_fix = partial(self.command_level_btn_fix)
        list_partial = [
            btn_level_select,

None,
            None,
            btn_level_fix]
        for i in range(len(list_button_name)):
            y1 = game_type_height_mid - type_height / 2
            y2 = game_type_height_mid + type_height / 2
            x1 = game_type_width_mid_list[i] - type_width / 2
            x2 = game_type_width_mid_list[i] + type_width / 2
            if i == 0 or i == 3:
                bt_game_type = Button_Canvas(canvas, x1, y1, x2, y2, list_button_name[i], 15, '#1e90ff', '#3399ff', 'game_type', None, list_game_type_img_bgm_path[cur_level - 1], 1.05, 0.95, 'w', list_partial[i], **('d_outline', 'd_fill', 'btn_type', 'image', 'image_path', 'zone_out', 'zone_in', 'anchor', 'command'))
            elif i == 1:
                bt_game_type = Entry_Canvas(canvas, (x1 + x2) / 2, (y1 + y2) / 2, type_width, type_height, str(self.life_value), str(self.life_value), '#3399ff', int(0.0078125 * scnWidth), 0, str(i), list_button_name[i], path_button_frame, **('text1', 'text2', 'd_fill', 'fontsize', 'outlineboder', 'flag', 'text3', 'image_path'))
                bt_game_type.editable(self.blood_editable)
                self.list_input_btn.append(bt_game_type)
            else:
                bt_game_type = Entry_Canvas(canvas, (x1 + x2) / 2, (y1 + y2) / 2, type_width, type_height, str(self.game_time), str(self.game_time), '#3399ff', int(0.0078125 * scnWidth), 0, str(i), list_button_name[i], path_button_frame, **('text1', 'text2', 'd_fill', 'fontsize', 'outlineboder', 'flag', 'text3', 'image_path'))
                bt_game_type.editable(self.time_editable)
                self.list_input_btn.append(bt_game_type)
            self.list_btn_level_slt.append(bt_game_type)
        

    
    def create_ranking_image(self):
        (scnWidth, scnHeight) = self.root_size
        img_process = self.img_process
        canvas = self.canvas_ranking
        path_img_bgm1 = './photo/game_main.png'
        path_img_ranking_frame = './photo/new/result_ranking_bg_frame1.png'
        path_img_ranking_title_btn = './photo/new/ranking_list_head_frame.png'
        path_img_ranking_num1 = './photo/new/result_ranking_one_frame.png'
        path_img_ranking_num2 = './photo/new/result_ranking_two_frame.png'
        path_img_ranking_num3 = './photo/new/result_ranking_three_frame.png'
        path_img_ranking_num4 = './photo/new/result_ranking_four_frame.png'
        path_img_ranking_num5 = './photo/new/result_ranking_five_frame.png'
        list_path_img_ranking = [
            path_img_ranking_num1,
            path_img_ranking_num2,
            path_img_ranking_num3,
            path_img_ranking_num4,
            path_img_ranking_num5]
        canvas_height = scnHeight * 9 / 20
        region = (0, canvas_height, scnWidth, scnHeight)
        self.img_ranking_bg = img_process.crop_img(path_img_bgm1, scnWidth, scnHeight, region)
        canvas.create_image(0, 0, 'nw', self.img_ranking_bg, 'background', **('anchor', 'image', 'tag'))
        width_start = 4
        tmp = 2.3
        bank_height = scnHeight * 2.2 / 32
        bank_width = scnWidth / 3
        ranking_num = 100000
        list_text = []
        list_text2 = []
        list_score = []
        if self.card_scan:
            
            try:
                result_list = self.db.search_game_result2(ranking_num)
                for result in result_list:
                    player_scode = str(result[0])
                    player_id = result[1].split(',')[0]
                    player_info = self.db.search_custom_tb_by_id(player_id)
                    if len(player_info) > 0:
                        player_info = player_info[0]
                        if len(player_info) > 2:
                            player_phone = player_info[1]
                            player_name = player_info[2]
                            str_tmp = '{:12s}'.format(player_name) + '{:15s}'.format(player_phone) + '{:5s}'.format(player_scode)
                            list_text.append(str_tmp)
                            list_score.append(result[0])
                        result_list = self.db.search_game_result_order_by_time(50)
                        for result in result_list:
                            player_scode = str(result[0])
                            player_id = result[2].split(',')[0]
                            player_info = self.db.search_custom_tb_by_id(player_id)
                            if len(player_info) > 0:
                                player_info = player_info[0]
                                if len(player_info) > 2:
                                    player_phone = player_info[1]
                                    player_name = player_info[2]
                                    
                                    try:
                                        tmp_ranking = '{:02d}'.format(list_score.index(result[0]) + 1) + '        '
                                    except:
                                        tmp_ranking = '          '

                                    str_tmp = tmp_ranking + '{:10s}'.format(player_name) + '{:15s}'.format(player_phone) + '{:10s}'.format(player_scode) + result[1].strftime('%Y-%m-%d %H:%M:%S')
                                    list_text2.append(str_tmp)
                        loguru.logger.info('db operation may be error')
                    
                
                try:
                    idx_name = 0
                    idx_scode = 1
                    text_color = 'yellow'
                    tourist_record = TouristRecord()
                    tourist_record.connect()
                    result = tourist_record.search(ranking_num, **('limit',))
                    result2 = tourist_record.search_rst_datetime(50, **('limit',))
                    tourist_record.close()
                    for i in range(len(result)):
                        
                        try:
                            custom_info = result[i][idx_name]
                            scode = str(result[i][idx_scode])
                            str_tmp = '{:30s}'.format(custom_info) + '{:5s}'.format(scode)
                            list_text.append(str_tmp)
                            list_score.append(result[i][idx_scode])
                        except:
                            pass

                    
                    for i in range(len(result2)):
                        
                        try:
                            custom_info = result2[i][idx_name]
                            scode = str(result2[i][idx_scode])
                            
                            try:
                                tmp_ranking = '{:02d}'.format(list_score.index(result2[i][idx_scode]) + 1) + '        '
                            except:
                                tmp_ranking = '          '

                            str_tmp = tmp_ranking + '{:30s}'.format(custom_info) + '{:10s}'.format(scode) + result2[i][2][:19]
                            list_text2.append(str_tmp)
                        except:
                            pass

                except:
                    loguru.logger.error(traceback.format_exc())

                size = self.root_size
                btn_width = size[0] / 12
                btn_height = size[1] / 24
                btn_back_x = size[0] / 8 - btn_width / 2
                btn_back_y = 0
                btn_next_x = size[0] - btn_back_x - btn_width
                btn_next_y = 0
                partial_back = partial(self.back)
                partial_next = partial(self.player_login)
                path_button_frame = './photo/new/result_ranking_bg_frame1.PNG'
                btn_back = Button_Canvas(canvas, btn_back_x, btn_back_y, btn_back_x + btn_width, btn_back_y + btn_height, language.BACK, 20, '#1e90ff', '#3399ff', 'game_type', None, path_button_frame, 1.05, 0.95, partial_back, **('d_outline', 'd_fill', 'btn_type', 'image', 'image_path', 'zone_out', 'zone_in', 'command'))
                btn_next = Button_Canvas(canvas, btn_next_x, btn_next_y, btn_next_x + btn_width, btn_next_y + btn_height, language.NEXT, 20, '#1e90ff', '#3399ff', 'game_type', None, path_button_frame, 1.05, 0.95, partial_next, **('d_outline', 'd_fill', 'btn_type', 'image', 'image_path', 'zone_out', 'zone_in', 'command'))
                self.list_btn_backornext += [
                    btn_back,
                    btn_next]
                coors = [
                    0,
                    scnHeight / 2]
                self.game_ranking = GameRankingCanvas(self.canvas, scnWidth / 2, scnHeight / 2 - 20, coors, self.root_size, list_text, self.card_scan, **('coors', 'screen_size', 'data', 'scan'))
                coors = [
                    scnWidth / 2,
                    scnHeight / 2]
                self.game_ranking2 = GameRankingCanvas(self.canvas, scnWidth / 2, scnHeight / 2 - 20, coors, self.root_size, list_text2, self.card_scan, False, **('coors', 'screen_size', 'data', 'scan', 'diff_bgi'))
                return None


    
            except:
                pass
    def create_ranking(self, frame):
        (scnWidth, scnHeight) = self.root_size
        img_process = self.img_process
        self.list_btn_backornext = []
        canvas = tkinter.Canvas(frame, scnWidth, scnHeight * 11 / 20, 0, 0, **('width', 'height', 'borderwidth', 'highlightthickness'))
        canvas.pack('center', **('anchor',))
        None(None, (lambda event = None: self.on_screen_click_back_next_btn(event, self.list_btn_backornext)))
        self.canvas_ranking = canvas
        thread = Thread(self.create_ranking_image, **('target',))
        thread.start()

    
    def ui_init_main_img_bgm(self):
        img_process = self.img_process
        canvas = self.canvas
        size = self.root_size
        path_img_bgm1 = './photo/game_main.png'
        self.image_game_level_bg = img_process.generate(path_img_bgm1, round(size[0]), round(size[1]))
        time_bft = time.time()
        canvas.create_image(size[0] / 2, size[1] / 2, 'center', self.image_game_level_bg, **('anchor', 'image'))
        print('gen img bg', time.time() - time_bft)

    
    def __init__(self, parent, cur_level):
        time_bft = time.time()
        root = tkinter.Toplevel()
        root.attributes('-fullscreen', Setting.FULL_SCREEN)
        size = root.maxsize()
        curWidth = size[0]
        curHeight = size[1]
        self.root_size = (curWidth, curHeight)
        self.cur_level = cur_level
        self.parent = parent
        self.db = parent.db
        self.life_value = parent.setting.life_value.get()
        self.game_time = parent.setting.game_time.get()
        self.editable = parent.setting.game_leval_editable.get()
        self.blood_editable = parent.setting.life_value_editable.get()
        self.time_editable = parent.setting.game_time_editable.get()
        self.list_list_btn = []
        self.list_game_level_btn_img_bgm_path = [
            './photo/game_type/1star.jpg',
            './photo/game_type/2star.jpg',
            './photo/game_type/3star.jpg']
        fm_main = tkinter.Frame(root)
        fm_main.pack()
        self.fm_main = fm_main
        self.card_scan = parent.setting.barcode_function.get()
        canvas = tkinter.Canvas(fm_main, curWidth, curHeight, 0, 0, **('width', 'height', 'borderwidth', 'highlightthickness'))
        canvas.pack('center', **('anchor',))
        None(None, (lambda event = None: self.on_screen_click_level_btn(event)))
        self.canvas = canvas
        fm_picture_2 = tkinter.Frame(canvas)
        fm_picture_2.grid(0, 0, **('row', 'column'))
        fm_picture_1 = tkinter.Frame(canvas)
        fm_picture_1.grid(0, 0, **('row', 'column'))
        fm_button = tkinter.Frame(canvas)
        fm_button.grid(2, 0, **('row', 'column'))
        fm_ranking = tkinter.Frame(canvas)
        fm_ranking.grid(3, 0, **('row', 'column'))
        self.fm_picture_1 = fm_picture_1
        self.fm_picture_2 = fm_picture_2
        self.img_process = ImageProcess()
        self.ui_init_main_img_bgm()
        list_game_leval = [
            language.LEVAL_SIMPLE,
            language.LEVAL_NORMAL,
            language.LEVAL_HARDER]
        self.create_game_level_slt(fm_picture_1, list_game_leval)
        self.create_game_level_fix(fm_picture_2, cur_level)
        self.create_level_select_button(fm_button, self.cur_level)
        self.create_ranking(fm_ranking)
        self.root = root
        root.update()
        (scnWidth, scnHeight) = root.maxsize()
        curWidth = scnWidth
        curHeight = scnHeight
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol('WM_DELETE_WINDOW', self.customized_function)
        root.iconbitmap('./photo/ledplay.ico')
        root.title(language.GAME_LEVAL)
        loguru.logger.info('in gui game level select')

    
    def player_login(self):
        self.parent.life_value = int(self.list_input_btn[0].value)
        self.parent.game_level = self.cur_level
        if self.parent.game_record_rt.game_time_pass == 0:
            self.parent.game_time = float(self.list_input_btn[1].value)
            self.parent.page3 = PlayerLogin(self)
            self.list_btn_backornext[1].focus_off()
            loguru.logger.info('out of gui PlayerLogin')
        else:
            GuiCountDown(self.parent, self)
            loguru.logger.info('out of gui countdown')

    
    def back(self):
        loguru.logger.info('game level select ui back button click')
        self.root.update()
        time.sleep(0.3)
        self.list_btn_backornext[0].focus_off()
        self.list_btn_backornext.clear()
        self.customized_function()
        self.parent.reset_after_game_time_out()

    
    def customized_function(self):
        self.root.destroy()


