# Source Generated with Decompyle++
# File: tourist_record_main.pyc (Python 3.7)

import shelve
from gui.language import language
from tourist_record.gui_game_result_tourist import GameResult
from tourist_record.tourist_info import Tourist
import subprocess
import sqlite3

class TouristRecord:
    PATH_DATA = './data/local_data.db'
    KEY_TOURIST = 'key_tourist'
    
    def __init__(self):
        pass

    
    def connect(self):
        self.conn = sqlite3.connect(TouristRecord.PATH_DATA)
        print('数据库打开成功')
        cursor = self.conn.cursor()
        self.cursor = cursor

    
    def close(self):
        self.cursor.close()
        self.conn.close()

    
    def get_row_count(self):
        cursor = self.cursor
        table_name = 'COMPANY'
        cursor.execute(f'''SELECT COUNT(*) FROM {table_name}''')
        row_count = cursor.fetchone()[0]
        return row_count

    
    def delete_table(self):
        sql = 'DROP TABLE COMPANY'
        self.cursor.execute(sql)
        self.conn.commit()

    
    def create_table(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS COMPANY\n               (NAME           TEXT    NOT NULL,\n               SCODE            REAL     NOT NULL,\n               DATETIME        DATETIME NOT NULL);\n               ')
        print('数据表创建成功')
        self.conn.commit()

    
    def add(self, tourist):
        sql = 'INSERT INTO COMPANY (NAME, SCODE, DATETIME) VALUES (?, ?, ?)'
        val = (tourist.name, tourist.scode, tourist.date)
        self.cursor.execute(sql, val)
        self.conn.commit()

    
    def search(self, limit = (1,)):
        sql = 'SELECT NAME,SCODE,DATETIME  FROM COMPANY ORDER BY SCODE DESC, DATETIME DESC LIMIT ' + str(limit)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    
    def search_rst_datetime(self, limit = (1,)):
        sql = 'SELECT NAME,SCODE,DATETIME  FROM COMPANY ORDER BY DATETIME DESC LIMIT ' + str(limit)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    
    def dispaly(self, parent, result, title, game_time, game_player_num, cur_scode, parent_game_running = (None, language.GAME_RESULT, 1, 1, 0, None)):
        GameResult(parent, result, title, game_time, game_player_num, cur_scode, parent_game_running)


