# Source Generated with Decompyle++
# File: game_util.pyc (Python 3.7)

import decimal
import math
import os
import random
import shelve
import shutil
import sys
import traceback
import zipfile
from loguru import logger
from model.group import Group
from model.setting import Setting, Color

class GameUtil:
    
    def __init(self):
        pass

    
    def get_game_speed(self, game_level, leval_span):
        if game_level <= 1:
            game_level_speed = 1 - leval_span
            if game_level_speed < 0:
                game_level_speed = 0.1
            elif game_level == 2:
                game_level_speed = 1
            else:
                game_level_speed = 1 + leval_span
        return game_level_speed

    
    def table_cut_vir(self, table, row, col, row_range, col_range = (None, None)):
        if not row_range:
            row_range = (0, row)
        elif row_range[0] < 0 or range[1] > row:
            row_range = (0, row)
        if not col_range:
            col_range = (0, col)
        elif col_range[0] < 0 or col_range[1] > col:
            col_range = (0, col)
        new_tabel = []
        for i in range(row_range[0], row_range[1]):
            new_tabel.append(table[i][col_range[0]:col_range[1]])
        

    
    def remove_file_after_zip(self, game_zip_path):
        
        try:
            shutil.rmtree(game_zip_path)
        except:
            logger.error(traceback.format_exc())


    
    def remove_unzipfile(self, game_name):
        
        try:
            relative_path = os.path.relpath(game_name)
            self.remove_file_after_zip(relative_path)
        except:
            pass


    
    def unzipfile(self, game_zip_path):
        game_unzip_dir = os.path.splitext(game_zip_path)[0]
        
        try:
            with zipfile.ZipFile(game_zip_path, 'r') as myzip:
                for file in myzip.namelist():
                    myzip.extract(file, game_unzip_dir, **('path',))
            myzip.close()
            ret = True
        except:
            ret = False

        return ret

    
    def get_video_path(self, music_folder, name):
        if name is not None and name != '' and name != 'None':
            return os.path.join(music_folder, name)
        return None

    
    def half_up(self, data):
        return int(decimal.Decimal(data).quantize(
            decimal.Decimal('0'), rounding=decimal.ROUND_HALF_UP))

    
    def get_max_end_time_in_all_group(self, dict_group):
        max_end_time = 0
        for key, value in dict_group.items():
            end_time = value.end_time_sec
            if end_time > max_end_time:
                max_end_time = end_time
        return max_end_time

    
    def move_range_zone_in_out(self, move_range, area_before, area_after = ([
        (0, Setting.ROW),
        (0, Setting.COL)], [
        (0, Setting.ROW),
        (0, Setting.COL)], [
        (0, Setting.ROW),
        (0, Setting.COL)])):
        (row_before, col_before) = area_before
        (row_after, col_after) = area_after
        multiple_row = row_after / row_before
        multiple_col = col_after / col_before
        zone_middle_row = (move_range[0][0] + move_range[0][1]) / 2
        zone_middle_col = (move_range[1][0] + move_range[1][1]) / 2
        zone_edge_row = (move_range[0][1] - move_range[0][0]) / 2
        zone_edge_col = (move_range[1][1] - move_range[1][0]) / 2
        zone_middle_row_new = zone_middle_row * multiple_row
        zone_middle_col_new = zone_middle_col * multiple_col
        zone_edge_row_new = zone_edge_row * multiple_row
        zone_edge_col_new = zone_edge_col * multiple_col
        zone_range_row_from = self.half_up(zone_middle_row_new - zone_edge_row_new)
        zone_range_row_to = self.half_up(zone_middle_row_new + zone_edge_row_new)
        zone_range_col_from = self.half_up(zone_middle_col_new - zone_edge_col_new)
        zone_range_col_to = self.half_up(zone_middle_col_new + zone_edge_col_new)
        move_range_new = [
            (zone_range_row_from, zone_range_row_to),
            (zone_range_col_from, zone_range_col_to)]
        return move_range_new

    
    def on_the_edge_of_row(self, coors_before, cell_set = ([], [])):
        row_edge = coors_before[0] - 1
        for coors in cell_set:
            row = coors[0]
            if row == 0:
                return 0
            if None == row_edge:
                return row_edge
        
        return -1

    
    def on_the_edge_of_col(self, coors_before, cell_set = ([], [])):
        col_edge = coors_before[1] - 1
        for coors in cell_set:
            col = coors[1]
            if col == 0:
                return 0
            if None == col_edge:
                return col_edge
        
        return -1

    
    def zone_in_out_old(self, coors_before, coors_after, cell_set, side = ([], [], None, Setting.SIDE_NONE)):
        border = 0
        cell_width = 30
        cell_high = 30
        if cell_set is not None:
            cell_set_after = set()
            (row_before, col_before) = coors_before
            (row_after, col_after) = coors_after
            multiple_row = row_after / row_before
            multiple_col = col_after / col_before
            for cell in cell_set:
                coors_row_middle_before = (2 * cell[0] + 1) / 2
                row_edge_before = 0.5
                coors_row_before_min = coors_row_middle_before
                coors_row_before_max = row_edge_before
                coors_col_middle_before = (2 * cell[1] + 1) / 2
                col_edge_before = 0.5
                coors_col_before_min = coors_col_middle_before
                coors_col_before_max = col_edge_before
                if side == Setting.SIDE_BOTH:
                    coors_row_after_min = coors_row_before_min * multiple_row
                    coors_row_after_max = coors_row_before_max * multiple_row
                    coors_col_after_min = coors_col_before_min * multiple_col
                    coors_col_after_max = coors_col_before_max * multiple_col
                    row_after_min = coors_row_after_min - coors_row_after_max
                    row_after_max = coors_row_after_min + coors_row_after_max
                    col_after_min = coors_col_after_min - coors_col_after_max
                    col_after_max = coors_col_after_min + coors_col_after_max
                    row_edge_after = coors_row_after_max
                    col_edge_after = coors_col_after_max
                elif side == Setting.SIDE_ROW:
                    coors_row_after_min = coors_row_before_min * multiple_row
                    coors_row_after_max = coors_row_before_max * multiple_row
                    row_after_min = coors_row_after_min - coors_row_after_max
                    row_after_max = coors_row_after_min + coors_row_after_max
                    on_the_edge = self.on_the_edge_of_col(coors_before, cell_set)
                    if on_the_edge == 0:
                        coors_col_after_min = cell[1]
                        coors_col_after_max = cell[1] + 1
                    elif on_the_edge > 0:
                        coors_col_after_min = col_after - col_before - cell[1]
                        coors_col_after_max = coors_col_after_min + 1
                    else:
                        coors_col_after_min = cell[1] + (col_after - col_before) / 2
                        coors_col_after_max = cell[1] + 1 + (col_after - col_before) / 2
                    col_after_min = coors_col_after_min
                    col_after_max = coors_col_after_max
                    row_edge_after = coors_row_after_max
                    col_edge_after = 0.5
                elif side == Setting.SIDE_COL:
                    coors_col_after_min = coors_col_before_min * multiple_col
                    coors_col_after_max = coors_col_before_max * multiple_col
                    col_after_min = coors_col_after_min - coors_col_after_max
                    col_after_max = coors_col_after_min + coors_col_after_max
                    on_the_edge = self.on_the_edge_of_row(coors_before, cell_set)
                    if on_the_edge == 0:
                        coors_row_after_min = cell[0]
                        coors_row_after_max = cell[0] + 1
                    elif on_the_edge > 0:
                        coors_row_after_min = row_after - row_before - cell[0]
                        coors_row_after_max = coors_row_after_min + 1
                    else:
                        coors_row_after_min = cell[0] + (row_after - row_before) / 2
                        coors_row_after_max = cell[0] + 1 + (row_after - row_before) / 2
                    row_after_min = coors_row_after_min
                    row_after_max = coors_row_after_max
                    row_edge_after = 0.5
                    col_edge_after = coors_col_after_max
                else:
                    on_the_edge = self.on_the_edge_of_col(coors_before, cell_set)
                    if on_the_edge == 0:
                        coors_col_after_min = cell[1]
                        coors_col_after_max = cell[1] + 1
                    elif on_the_edge > 0:
                        coors_col_after_min = col_after - col_before - cell[1]
                        coors_col_after_max = coors_col_after_min + 1
                    else:
                        coors_col_after_min = cell[1] + (col_after - col_before) / 2
                        coors_col_after_max = cell[1] + 1 + (col_after - col_before) / 2
                    on_the_edge = self.on_the_edge_of_row(coors_before, cell_set)
                    if on_the_edge == 0:
                        coors_row_after_min = cell[0]
                        coors_row_after_max = cell[0] + 1
                    elif on_the_edge > 0:
                        coors_row_after_min = row_after - row_before - cell[0]
                        coors_row_after_max = coors_row_after_min + 1
                    else:
                        coors_row_after_min = cell[0] + (row_after - row_before) / 2
                        coors_row_after_max = cell[0] + 1 + (row_after - row_before) / 2
                    row_after_min = coors_row_after_min
                    row_after_max = coors_row_after_max
                    col_after_min = coors_col_after_min
                    col_after_max = coors_col_after_max
                    row_edge_after = 0.5
                    col_edge_after = 0.5
                row_after_min = self.half_up(round(row_after_min, 2))
                row_after_max = self.half_up(round(row_after_max, 2))
                col_after_min = self.half_up(round(col_after_min, 2))
                col_after_max = self.half_up(round(col_after_max, 2))
                int_row_after_min = self.half_up(row_after_min)
                if row_after_min < 0:
                    row_after_min = 0
                if row_after_min >= row_after:
                    row_after_min = row_after - 1
                if row_after_max > row_after:
                    row_after_max = row_after
                if row_after_max <= 0:
                    row_after_max = 1
                if col_after_min < 0:
                    col_after_min = 0
                if col_after_min >= col_after:
                    col_after_min = col_after - 1
                if col_after_max > col_after:
                    col_after_max = col_after
                if col_after_max <= 0:
                    col_after_max = 1
                if row_after_min == row_after_max:
                    row_after_max = row_after_min + 1
                if col_after_min == col_after_max:
                    col_after_max = col_after_min + 1
                for i in range(row_after_min, row_after_max):
                    for j in range(col_after_min, col_after_max):
                        cell_set_after.add((i, j))
                    
                
            
            return cell_set_after
        return None

    
    def zone_in_out(self, coors_before, coors_after, cell_set, side = ([], [], None, Setting.SIDE_NONE)):
        if cell_set is not None:
            cell_set_after = set()
            (row_before, col_before) = coors_before
            (row_after, col_after) = coors_after
            multiple_row = row_after / row_before
            multiple_col = col_after / col_before
            (min_row, max_row) = (10000, 1)
            (min_col, max_col) = (10000, 1)
            for cell in cell_set:
                if cell[0] < min_row:
                    min_row = cell[0]
                if cell[0] > max_row:
                    max_row = cell[0]
                if cell[1] < min_col:
                    min_col = cell[1]
                if cell[1] > max_col:
                    max_col = cell[1]
            cen_row = (min_row + max_row) / 2
            cen_col = (min_col + max_col) / 2
            center_col_after = cen_col * multiple_col
            center_row_after = cen_row * multiple_row
            for cell in cell_set:
                coors_row_middle_before = (2 * cell[0] + 1) / 2
                row_edge_before = 0.5
                coors_row_before_min = coors_row_middle_before
                coors_row_before_max = row_edge_before
                coors_col_middle_before = (2 * cell[1] + 1) / 2
                col_edge_before = 0.5
                coors_col_before_min = coors_col_middle_before
                coors_col_before_max = col_edge_before
                if side == Setting.SIDE_BOTH:
                    coors_row_after_min = coors_row_before_min * multiple_row
                    coors_row_after_max = coors_row_before_max * multiple_row
                    coors_col_after_min = coors_col_before_min * multiple_col
                    coors_col_after_max = coors_col_before_max * multiple_col
                    row_after_min = coors_row_after_min - coors_row_after_max
                    row_after_max = coors_row_after_min + coors_row_after_max
                    col_after_min = coors_col_after_min - coors_col_after_max
                    col_after_max = coors_col_after_min + coors_col_after_max
                    row_edge_after = coors_row_after_max
                    col_edge_after = coors_col_after_max
                elif side == Setting.SIDE_ROW:
                    coors_row_after_min = coors_row_before_min * multiple_row
                    coors_row_after_max = coors_row_before_max * multiple_row
                    row_after_min = coors_row_after_min - coors_row_after_max
                    row_after_max = coors_row_after_min + coors_row_after_max
                    on_the_edge = self.on_the_edge_of_col(coors_before, cell_set)
                    if on_the_edge == 0:
                        coors_col_after_min = cell[1]
                        coors_col_after_max = cell[1] + 1
                    elif on_the_edge > 0:
                        coors_col_after_min = col_after - col_before - cell[1]
                        coors_col_after_max = coors_col_after_min + 1
                    else:
                        coors_col_after_min = (cell[1] - cen_col) + center_col_after
                        coors_col_after_max = (cell[1] - cen_col) + center_col_after + 1
                    col_after_min = coors_col_after_min
                    col_after_max = coors_col_after_max
                    row_edge_after = coors_row_after_max
                    col_edge_after = 0.5
                elif side == Setting.SIDE_COL:
                    coors_col_after_min = coors_col_before_min * multiple_col
                    coors_col_after_max = coors_col_before_max * multiple_col
                    col_after_min = coors_col_after_min - coors_col_after_max
                    col_after_max = coors_col_after_min + coors_col_after_max
                    on_the_edge = self.on_the_edge_of_row(coors_before, cell_set)
                    if on_the_edge == 0:
                        coors_row_after_min = cell[0]
                        coors_row_after_max = cell[0] + 1
                    elif on_the_edge > 0:
                        coors_row_after_min = row_after - row_before - cell[0]
                        coors_row_after_max = coors_row_after_min + 1
                    else:
                        coors_row_after_min = (cell[0] - cen_row) + center_row_after
                        coors_row_after_max = (cell[0] - cen_row) + center_row_after + 1
                    row_after_min = coors_row_after_min
                    row_after_max = coors_row_after_max
                    row_edge_after = 0.5
                    col_edge_after = coors_col_after_max
                else:
                    on_the_edge = self.on_the_edge_of_col(coors_before, cell_set)
                    if on_the_edge == 0:
                        coors_col_after_min = cell[1]
                        coors_col_after_max = cell[1] + 1
                    elif on_the_edge > 0:
                        coors_col_after_min = col_after - col_before - cell[1]
                        coors_col_after_max = coors_col_after_min + 1
                    else:
                        coors_col_after_min = (cell[1] - cen_col) + center_col_after
                        coors_col_after_max = (cell[1] - cen_col) + center_col_after + 1
                    on_the_edge = self.on_the_edge_of_row(coors_before, cell_set)
                    if on_the_edge == 0:
                        coors_row_after_min = cell[0]
                        coors_row_after_max = cell[0] + 1
                    elif on_the_edge > 0:
                        coors_row_after_min = row_after - row_before - cell[0]
                        coors_row_after_max = coors_row_after_min + 1
                    else:
                        coors_row_after_min = (cell[0] - cen_row) + center_row_after
                        coors_row_after_max = (cell[0] - cen_row) + center_row_after + 1
                    row_after_min = coors_row_after_min
                    row_after_max = coors_row_after_max
                    col_after_min = coors_col_after_min
                    col_after_max = coors_col_after_max
                    row_edge_after = 0.5
                    col_edge_after = 0.5
                row_after_min = self.half_up(round(row_after_min, 2))
                row_after_max = self.half_up(round(row_after_max, 2))
                col_after_min = self.half_up(round(col_after_min, 2))
                col_after_max = self.half_up(round(col_after_max, 2))
                int_row_after_min = self.half_up(row_after_min)
                if row_after_min < 0:
                    row_after_min = 0
                if row_after_max > row_after:
                    row_after_max = row_after
                if col_after_min < 0:
                    col_after_min = 0
                if col_after_max > col_after:
                    col_after_max = col_after
                if row_after_min == row_after_max:
                    if row_after_min < row_after:
                        row_after_max = row_after_min + 1
                    else:
                        row_after_min = row_after_max - 1
                if col_after_min == col_after_max:
                    if col_after_min < col_after:
                        col_after_max = col_after_min + 1
                    else:
                        col_after_min = col_after_max - 1
                for i in range(row_after_min, row_after_max):
                    for j in range(col_after_min, col_after_max):
                        cell_set_after.add((i, j))
                    
                
            
            return cell_set_after
        return None

    
    def group_area_transform(self, game, tmp_dict_group, setting):
        last_game_exist_wall = False
        cur_game_exist_wall = False
        last_game_area_adaption = game.game_area_adaption
        layout_row = int(setting.value_high.get())
        layout_col = int(setting.value_width.get())
        corner_line_start = setting.corner_line_start.get()
        if game.corner_line_start > 0:
            last_game_exist_wall = True
        if corner_line_start > 0:
            cur_game_exist_wall = True
        if cur_game_exist_wall and last_game_exist_wall:
            for key, group in tmp_dict_group.items():
                if group.start_area == 1:
                    new_group_member = []
                    for coors in group.start_member:
                        new_group_member.append((coors[0], coors[1] - game.corner_line_start))
                    
                    group.start_member = new_group_member
                group_col_from = group.activity_area[1][0]
                group_col_to = group.activity_area[1][1]
                if group_col_from >= game.corner_line_start:
                    size_floor_before = [
                        game.row,
                        game.col - game.corner_line_start]
                    size_floor_after = [
                        layout_row,
                        layout_col - corner_line_start]
                    group.activity_area[1] = (group.activity_area[1][0] - game.corner_line_start, group.activity_area[1][1] - game.corner_line_start)
                    group.activity_area = self.move_range_zone_in_out(group.activity_area, size_floor_before, size_floor_after)
                    group.activity_area[1] = (corner_line_start + group.activity_area[1][0], corner_line_start + group.activity_area[1][1])
                    continue
                if group_col_to <= game.corner_line_start:
                    size_wall_before = [
                        game.row,
                        game.corner_line_start]
                    size_wall_after = [
                        layout_row,
                        corner_line_start]
                    group.activity_area = self.move_range_zone_in_out(group.activity_area, size_wall_before, size_wall_after)
                    continue
                size_wall_before = [
                    game.row,
                    game.corner_line_start]
                size_wall_after = [
                    layout_row,
                    corner_line_start]
                activity_area_wall = [
                    group.activity_area[0],
                    (group.activity_area[1][0], game.corner_line_start)]
                activity_area_wall = self.move_range_zone_in_out(activity_area_wall, size_wall_before, size_wall_after)
                size_floor_before = [
                    game.row,
                    game.col - game.corner_line_start]
                size_floor_after = [
                    layout_row,
                    layout_col - corner_line_start]
                activity_area_floor = [
                    group.activity_area[0],
                    (group.activity_area[1][0] - game.corner_line_start, group.activity_area[1][1] - game.corner_line_start)]
                activity_area_floor = self.move_range_zone_in_out(activity_area_floor, size_floor_before, size_floor_after)
                group.activity_area = [
                    activity_area_wall[0],
                    (activity_area_wall[1][0], activity_area_floor[1][1] + corner_line_start)]
            
        elif cur_game_exist_wall and last_game_exist_wall:
            if last_game_area_adaption:
                for key, group in tmp_dict_group.items():
                    if group.start_area == 0:
                        group.start_area = 1
                    size_before = [
                        game.row,
                        game.col]
                    size_after = [
                        layout_row,
                        layout_col]
                    group.activity_area = self.move_range_zone_in_out(group.activity_area, size_before, size_after)
                
            else:
                game.col = game.col - game.corner_line_start
                for key, group in tmp_dict_group.items():
                    if group.start_area == 1:
                        new_group_member = []
                        for coors in group.start_member:
                            new_group_member.append((coors[0], coors[1] - game.corner_line_start))
                        
                        group.start_member = new_group_member
                        size_before = [
                            game.row,
                            game.col]
                        size_after = [
                            layout_row,
                            layout_col]
                        group.activity_area[1] = (group.activity_area[1][0] - game.corner_line_start, group.activity_area[1][1] - game.corner_line_start)
                        group.activity_area = self.move_range_zone_in_out(group.activity_area, size_before, size_after)
                    elif group.type == Setting.FLOOR_LIGHT:
                        group.start_member = []
                return True
        if not cur_game_exist_wall and last_game_exist_wall:
            for key, group in tmp_dict_group.items():
                size_before = [
                    game.row,
                    game.col]
                size_after = [
                    layout_row,
                    layout_col - corner_line_start]
                group.activity_area = self.move_range_zone_in_out(group.activity_area, size_before, size_after)
                group.activity_area[1] = (corner_line_start + group.activity_area[1][0], corner_line_start + group.activity_area[1][1])
            
        else:
            for key, group in tmp_dict_group.items():
                size_before = [
                    game.row,
                    game.col]
                size_after = [
                    layout_row,
                    layout_col]
                group.activity_area = self.move_range_zone_in_out(group.activity_area, size_before, size_after)
            
        return True

    
    def group_size_scale(self, game, dict_group, setting):
        row = int(setting.value_high.get())
        col = int(setting.value_width.get())
        platform_size = [
            row,
            col]
        layout_corner_line_start = setting.corner_line_start.get()
        if not self.group_area_transform(game, dict_group, setting):
            return False
        for key in dict_group.keys():
            group = dict_group[key]
            group_member = self.zone_in_out([
                game.row,
                game.col], platform_size, group.start_member, group.scale)
            group.start_member = group_member
        if group.start_area == 0:
            group_member = self.zone_in_out([
                game.row,
                game.corner_line_start], [
                platform_size[0],
                layout_corner_line_start], group.start_member, group.scale)
            group.start_member = group_member
        else:
            group_member = self.zone_in_out([
                game.row,
                game.col - game.corner_line_start], [
                platform_size[0],
                platform_size[1] - layout_corner_line_start], group.start_member, group.scale)
            new_grop_member = []
            if group_member is not None:
                for coors in group_member:
                    new_grop_member.append((coors[0], coors[1] + setting.corner_line_start.get()))
                
            group.start_member = new_grop_member
        for coors in group.start_member.copy():
            if group.speed == 0 and coors in setting.floor_layout_coors_no_use:
                group.start_member.remove(coors)
            arr_no_use = setting.wall_posi_del.get().split(',')
            if '' in arr_no_use:
                arr_no_use.remove('')
            arr_no_use = (lambda _iter_: [ int(i) - 1 for i in _iter_ ])(arr_no_use)
            for position in group.start_member.copy():
                if position in arr_no_use:
                    index = group.start_member.index(position)
                    group.start_member.pop(index)
                    if group.text is not None and len(group.text) > 0:
                        
                        try:
                            group.text.pop(index)
                        except:
                            logger.error('wall screen group member and text may not corresponding ')

                row_resize = row / game.row
                col_resize = col / game.col
                tmp = round(game.zone_row_from * row_resize)
                game.zone_row_from = tmp
                tmp = round(game.zone_col_from * col_resize)
                game.zone_col_from = tmp
                game.zone_row_to = round(game.zone_row_to * row_resize)
                game.zone_col_to = round(game.zone_col_to * col_resize)
                return True

    
    def init_running_dict_group(self, dict_group_edict, parallel_dict_group = (None,)):
        if parallel_dict_group is not None:
            for key, group in parallel_dict_group.items():
                dict_group_edict[key + '_parallel'] = group
            
        return dict_group_edict

    
    def read_game_parameter_game_frag(self, game_path, game_frag_relpath, setting):
        pass
