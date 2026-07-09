# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.14.4 (main, Apr  7 2026, 13:13:20) [Clang 17_iter__iter_ (clang-1700.6.4.2)]
# Embedded file name: gui_wall_light_position_setting.py
from tkinter import Toplevel, ttk, LEFT
import gui.language as language
from model.setting import Setting

class WallLightSetting:

    def comform(self, parent):
        print("new game_play comform click")
        str_tmp = language.WALL_LAYOUT + "\n" + language.WALL_LAYOUT_START + ":" + str(parent.wall_start.get()) + "\n" + language.WALL_LAYOUT_DIRECTION + ":" + parent.wall_direct.get() + "\n" + language.WALL_LAYOUT_DELETE + ":" + parent.wall_posi_del.get()
        parent.wall_setting_text.set(str_tmp)
        parent.set_wall_light_layout_array(int(parent.value_high.get()), int(parent.value_width.get()))
        self.root.destroy()

    def __init__(self, parent):
        print("in new game_play")
        self.root = Toplevel()
        root = self.root
        fm_wall = ttk.Frame(root)
        fm_wall.pack()
        ttk.Label(fm_wall, text=(language.WALL_LAYOUT)).grid(row=0, column=0)
        fm_canvas = ttk.Frame(root)
        fm_canvas.pack()
        parent.draw_table_canvas(fm_canvas, int(parent.value_high.get()) + 2, int(parent.value_width.get()) + 2)
        ttk.Label(fm_wall, text=(language.WALL_LAYOUT_START)).grid(row=2, column=0)
        ttk.Entry(fm_wall, textvariable=(parent.wall_start)).grid(row=2, column=1)
        ttk.Label(fm_wall, text=(language.WALL_LAYOUT_DIRECTION)).grid(row=3, column=0)
        ttk.Combobox(fm_wall, textvariable=(parent.wall_direct), values=["right", "left"], width=15).grid(row=3, column=1)
        ttk.Label(fm_wall, text=(language.WALL_LAYOUT_DELETE)).grid(row=4, column=0)
        ttk.Entry(fm_wall, textvariable=(parent.wall_posi_del)).grid(row=4, column=1)
        btn = ttk.Button(root, text=(language.CONFIRM), command=(lambda: self.comform(parent)))
        btn.pack()
        root.update()
        curWidth = root.winfo_width()
        curHeight = root.winfo_height()
        scnWidth, scnHeight = root.maxsize()
        tmpcnf = "+%d+%d" % ((scnWidth - curWidth) / 2, (scnHeight - curHeight) / 2)
        root.geometry(tmpcnf)
        root.protocol("WM_DELETE_WINDOW", self.customized_function)
        root.iconbitmap("./photo/ledplay.ico")
        root.title("墙灯布局")
        root.grab_set()
        root.mainloop()

    def customized_function(self):
        self.root.destroy()

# okay decompiling /Users/apple/Desktop/activerse/climb/climb_source_code/gui/gui_wall_light_position_setting.pyc
