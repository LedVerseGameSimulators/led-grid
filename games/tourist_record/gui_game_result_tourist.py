# Source Generated with Decompyle++
# File: gui_game_result_tourist.pyc (Python 3.7)

import json
import shelve
import time
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image
from tkinter.font import font as tf
import tkinter
from loguru import logger
from database.db_operation import DBOperation
from gui.gui_game_ranking_canvas import GameRankingCanvas
from gui.language import language
from gui2.ui_table import Table
from model.setting import Setting
from ui_design.button_canvas import Button_Canvas
from ui_design.entry_canvas import Entry_Canvas

class GameResult:
    
    def btn_comform(self):
        pass

    
    def update_data_ui(self, scode, life_vale):
        cur_length = life_vale * self.length_rect / 100
        self.canvas.itemconfig(self.text_scode_value, str(scode), **('text',))

    
    def title_canvas_keypress(self, event, list_item):
        canvas = event.widget
        for item in list_item:
            str_char = '{0}'.format(event.char)
            event = [
                event.x,
                event.y]
            item.input(str_char)
        

    
    def title_canvas_click(self, event, list_item):
        canvas = event.widget
        if canvas.gettags('current') == canvas.gettags('close'):
            logger.info('local game result ui close button click')
            self.customized_function()
        else:
            for item in list_item:
                str_char = '{0}'.format(event.char)
                event = [
                    event.x,
                    event.y]
                item.Focus(event, str_char, **('str_char',))
            

    
    def draw_background(self, canvas, scnWidth, scnHeight):
        image_title = Image.open('./photo/game_result.png')
        scale_width = image_title.width
        scal_height = image_title.height
        image_title = image_title.resize((scnWidth, scnHeight), Image.ANTIALIAS)
        self.image_file_title = ImageTk.PhotoImage(image_title)
        canvas.create_image(scnWidth / 2, scnHeight / 2, self.image_file_title, **('image',))
        scale_width = image_title.width / scale_width
        scal_height = image_title.height / scal_height
        image_title = Image.open('./photo/new/result_head_frame.png')
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_head_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image(0.5 * scnWidth, 0.0824074 * scnHeight, self.result_head_frame, **('image',))
        image_title = Image.open('./photo/new/result_ranking_bg_frame1.png')
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_ranking_bg_frame1 = ImageTk.PhotoImage(image_title)
        canvas.create_image(0.5 * scnWidth, 0.564815 * scnHeight, self.result_ranking_bg_frame1, **('image',))
        image_title = Image.open('./photo/new/ranking_list_head_frame.png')
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.ranking_list_head_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image(0.502604 * scnWidth, 0.224074 * scnHeight, self.ranking_list_head_frame, **('image',))
        image_title = Image.open('./photo/new/result_ranking_bg_frame2.png')
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_ranking_bg_frame2 = ImageTk.PhotoImage(image_title)
        canvas.create_image(0.147917 * scnWidth, 0.351852 * scnHeight, self.result_ranking_bg_frame2, 'nw', **('image', 'anchor'))
        image_title = Image.open('./photo/new/result_grade_frame.png')
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_grade_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image(0.239063 * scnWidth, 0.44537 * scnHeight, self.result_grade_frame, **('image',))
        image_title = Image.open('./photo/new/result_scode_frame.png')
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_scode_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image(0.241667 * scnWidth, 0.572222 * scnHeight, self.result_scode_frame, **('image',))
        image_title = Image.open('./photo/new/result_ranking_frame.png')
        image_title = image_title.resize((int(image_title.width * scale_width), int(scal_height * image_title.height)), Image.ANTIALIAS)
        self.result_ranking_frame = ImageTk.PhotoImage(image_title)
        canvas.create_image(0.240625 * scnWidth, 0.694444 * scnHeight, self.result_ranking_frame, **('image',))
        image_title = Image.open('./photo/300.png')
        image_title = image_title.resize((30, 30), Image.ANTIALIAS)
        self.image_close = ImageTk.PhotoImage(image_title)
        canvas.create_image(scnWidth, 0, 'ne', self.image_close, 'close', **('anchor', 'image', 'tag'))
        color_2 = 'white'
        canvas.create_text(0.239063 * scnWidth, 0.44537 * scnHeight, language.LEVEL, ('STKaiti', int(0.0130208 * scnWidth)), color_2, **('text', 'font', 'fill'))
        canvas.create_text(0.241667 * scnWidth, 0.572222 * scnHeight, language.SCORE, ('STKaiti', int(0.0130208 * scnWidth)), color_2, **('text', 'font', 'fill'))
        canvas.create_text(0.240625 * scnWidth, 0.694444 * scnHeight, language.GAME_RANK, ('STKaiti', int(0.0130208 * scnWidth)), color_2, **('text', 'font', 'fill'))
        canvas.create_text(0.502083 * scnWidth, 0.225926 * scnHeight, language.PLAY_RANKING_LIST, ('STKaiti', int(0.0130208 * scnWidth), 'bold'), color_2, **('text', 'font', 'fill'))

    
    def __init__(self, parent, result, title, game_time, game_player_num, cur_scode, parent_game_running = (None, language.GAME_RESULT, 1, 1, 0, None)):
        self.root = tkinter.Toplevel(parent.root, **('master',))
        root = self.root
        root.attributes('-topmost', 'true')
        self.parent = parent
        self.game_running_root = parent_game_running
        self.parent.game_record_rt.running_to_obj = self
        self.parent.game_record_rt.running_to_flag = 2
        if Setting.USE_SERIAL_HD:
            root.attributes('-fullscreen', True)
        color = '#CCFFFF'
        (scnWidth, scnHeight) = root.maxsize()
        frame_head = Frame(root)
        frame_head.pack(True, BOTH, **('expand', 'fill'))
        base_line = scnHeight / 3
        canvas = Canvas(frame_head, base_line, scnWidth, **('height', 'width'))
        canvas.pack(True, BOTH, **('expand', 'fill'))
        self.list_item = []
        canvas.focus_set()
        None(None, (lambda event = None: self.title_canvas_keypress(event, self.list_item)))
        None(None, (lambda event = None: self.title_canvas_click(event, self.list_item)))
        self.draw_background(canvas, scnWidth, scnHeight)
        entry_canvas = Entry_Canvas(canvas, scnWidth / 2, 0.0833333 * scnHeight, 0.125 * scnWidth, 0.05 * scnHeight, title, title, color, '#66ffff', int(0.015625 * scnWidth), 0, **('d_outline', 'd_fill', 'fontsize', 'outlineboder'))
        entry_canvas.value = title
        self.list_item.append(entry_canvas)
        self.image_rank = []
        gap = 10
        text_color = 'yellow'
        if game_time == 0:
            game_time = 1
        rank_num = len(result)
        list_text = []
        idx_name = 0
        idx_scode = 1
        idx_date = 2
        for i in range(rank_num):
            
            try:
                custom_info = result[i][idx_name]
                start_width = 0.763889 * scnWidth
                start_height = 0.402222 * scnHeight
                scode = result[i][idx_scode]
                list_text.append('{:30s}'.format(custom_info) + str(scode))
            except:
                pass

        
        self.game_ranking = GameRankingCanvas(canvas, scnWidth * 2 / 5, scnHeight / 2, [
            scnWidth * 1 / 2,
            scnHeight * 3 / 10], (scnWidth, scnHeight), list_text, False, './photo/game_result.png', **('coors', 'screen_size', 'data', 'title', 'bg_img_path'))
        j = 0
        text_color = '#66ffff'
        for j in range(len(result)):
            scode = result[j][idx_scode]
            if cur_scode >= scode:
                custom_scode = cur_scode
                ranking_star = round(((len(result) - (j + 1)) / len(result)) * 5)
                image = Image.open('./photo/xingxing.png')
                height = 30
                image = image.resize((height, height), Image.ANTIALIAS)
                if ranking_star < 1:
                    ranking_star = 1
            for i in range(ranking_star):
                self.image_rank.append(ImageTk.PhotoImage(image))
                start_height = 4 * scnHeight / 9
                start_width = 443 * scnWidth / 1440
                between_width = image.width * 1.5
                canvas.create_image(start_width + i * between_width, start_height, self.image_rank[i], **('image',))
            
            start_width = 528 * scnWidth / 1440
            start_height = 517 * scnHeight / 900
            canvas.create_text(start_width, start_height, str(custom_scode), ('STKaiti', int(0.0208333 * scnWidth)), text_color, **('text', 'font', 'fill'))
            start_width = 528 * scnWidth / 1440
            start_height = 630 * scnHeight / 900
            canvas.create_text(start_width, start_height, str(j + 1), ('STKaiti', int(0.0208333 * scnWidth)), text_color, **('text', 'font', 'fill'))
            if self.parent.game_record_rt.game_state == Setting.GAME_NORMAL_REMOTE:
                net_ret_result = [
                    'RESULT',
                    self.game_running_root.player_list[0],
                    game_player_num,
                    self.game_running_root.setting.game_leval.get(),
                    game_time,
                    scode,
                    j + 1]
                self.parent.last_player_ranking = j + 1
                self.parent.socket_net.send(net_ret_result)
        
        root.update()
        root.state('zoomed')
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        (scnWidth, scnHeight) = root.maxsize()
        tmpcnf = '+%d+%d' % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol('WM_DELETE_WINDOW', self.customized_function)
        root.iconbitmap('./photo/ledplay.ico')
        while self.root:
            time.sleep(0.05)
            root.update()

    
    def customized_function(self):
        self.root.destroy()
        self.root = None
        if self.game_running_root:
            self.game_running_root.customized_function()


