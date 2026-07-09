# Source Generated with Decompyle++
# File: ui_table.pyc (Python 3.7)

import tkinter
from tkinter import Frame, RIGHT, Y, BOTTOM, X, ttk, NO, CENTER
from tkinter.ttk import Scrollbar, Treeview

class Table:
    
    def clear(self):
        x = self.my_game.get_children()
        for item in x:
            self.my_game.delete(item)
        

    
    def reflesh_data(self, col_title, data = ([], [])):
        self.clear()
        self.refresh_col_title(col_title)
        row_id = 0
        for val in data:
            self.my_game.insert('', 'end', row_id, '', val, **('parent', 'index', 'iid', 'text', 'values'))
            row_id += 1
        

    
    def refresh_col_title(self, col_title = ([],)):
        self.my_game['columns'] = col_title
        self.my_game.column('#0', 0, NO, **('width', 'stretch'))
        self.my_game.heading('#0', '', CENTER, **('text', 'anchor'))
        for col in col_title:
            self.my_game.column(col, CENTER, 120, 50, **('anchor', 'width', 'minwidth'))
            self.my_game.heading(col, col, CENTER, **('text', 'anchor'))
        

    
    def __init__(self, root, col_title, data = ([], [])):
        game_frame = Frame(root, 800, **('width',))
        game_frame.pack()
        self.col_title = col_title
        game_scroll_ver = Scrollbar(game_frame, 'vertical', **('orient',))
        game_scroll_ver.pack(RIGHT, Y, **('side', 'fill'))
        game_scroll = Scrollbar(game_frame, 'horizontal', **('orient',))
        game_scroll.pack(BOTTOM, X, **('side', 'fill'))
        my_game = Treeview(game_frame, game_scroll_ver.set, game_scroll.set, **('yscrollcommand', 'xscrollcommand'))
        my_game.pack()
        self.my_game = my_game
        game_scroll_ver.config(my_game.yview, **('command',))
        game_scroll.config(my_game.xview, **('command',))
        my_game['columns'] = col_title
        my_game.column('#0', 0, NO, **('width', 'stretch'))
        my_game.heading('#0', '', CENTER, **('text', 'anchor'))
        for col in col_title:
            my_game.column(col, CENTER, 120, 50, **('anchor', 'width', 'minwidth'))
            my_game.heading(col, col, CENTER, **('text', 'anchor'))
        
        row_id = 0
        for val in data:
            my_game.insert('', 'end', row_id, '', val, **('parent', 'index', 'iid', 'text', 'values'))
            row_id += 1
        


