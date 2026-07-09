# Source Generated with Decompyle++
# File: db_operation.pyc (Python 3.7)

import mysql.connector as mysql

class DBOperation:
    
    def connect_db(self, ip_address = ('localhost',)):
        self.mydb = mysql.connector.connect(ip_address, 'root', 'root', 'ledplaydb', **('host', 'user', 'passwd', 'database'))
        print(self.mydb)
        mycursor = self.mydb.cursor()
        mycursor.execute('SHOW TABLES')
        self.cursor = mycursor
        table_name = []
        for x in mycursor:
            table_name.append(x[0])
            print(x)
        
        return table_name

    
    def insert_to_table_custom_tb(self, phone, name, rank, time_left):
        sql = 'INSERT INTO custom_info (phone_num, name, public, time_left) VALUES (%s, %s, %s, %s)'
        val = (phone, name, rank, time_left)
        result = self.cursor.execute(sql, val)
        print('result', result)
        self.mydb.commit()
        return self.cursor.rowcount

    
    def search_custom_tb_by_id(self, custom_id):
        sql = 'SELECT * FROM custom_info WHERE custom_id = %s'
        val = (custom_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    
    def search_custom_by_phone(self, phone_num):
        sql = 'SELECT * FROM custom_info WHERE phone_num = %s'
        val = (phone_num,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    
    def search_custom_by_field(self, field, value):
        sql = 'SELECT * FROM custom_info WHERE ' + field + ' = %s'
        val = (value,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    
    def search_custom_tb_by_id_and_phone(self, custom_id, phone_num):
        sql = 'SELECT * FROM custom_info WHERE custom_id = %s and phone_num = %s'
        val = (custom_id, phone_num)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    
    def search_recharge_tb_by_id(self, custom_id):
        sql = 'SELECT * FROM recharge_record WHERE custom_id = %s'
        val = (custom_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    
    def insert_to_table_recharge_record(self, custom_id, money, game_time, date):
        sql = 'INSERT INTO recharge_record (custom_id, money, game_time, date) VALUES (%s, %s, %s, %s)'
        val = (custom_id, money, game_time, date)
        result = self.cursor.execute(sql, val)
        print('result', result)
        self.mydb.commit()
        return self.cursor.rowcount

    
    def search_from_table(self, table):
        sql = 'select * from ' + table
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        print(result)
        return result

    
    def update_custom_tb_delete(self, custom_id, phone_num, name, public, time_left):
        sql = 'UPDATE custom_info SET phone_num = %s, name = %s, public = %s, time_left = %s WHERE custom_id = %s'
        val = (phone_num, name, public, time_left, custom_id)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        print(self.cursor.rowcount, ' 条记录被修改')
        return self.cursor.rowcount

    
    def update_custom_info_by_id(self, custom_id, phone_num, name, public, time_left = (None, None, None, None)):
        sql = 'UPDATE custom_info SET'
        val = []
        if phone_num is not None:
            sql += ' phone_num = %s,'
            val.append(phone_num)
        if name is not None:
            sql += ' name = %s,'
            val.append(name)
        if public is not None:
            sql += ' public = %s,'
            val.append(public)
        if time_left is not None:
            sql += ' time_left = %s,'
            val.append(time_left)
        sql = sql[:-1]
        sql += ' WHERE custom_id = %s'
        val.append(custom_id)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        print(self.cursor.rowcount, ' 条记录被修改')
        return self.cursor.rowcount

    
    def get_table_title(self, table):
        list_col = []
        sql = 'select * from ' + table
        self.cursor.execute(sql)
        self.cursor.fetchall()
        desc = self.cursor.description
        for field in desc:
            list_col.append(field[0])
        
        return list_col

    
    def get_table_name(self):
        return self.table_name

    
    def insert_custom_comsume(self, custom_id, game_consume_id, person_num, game_time, consume_time):
        sql = 'INSERT INTO custom_comsume (custom_id, comsume_id, member, game_time, comsume_time) VALUES (%s, %s, %s, %s, %s)'
        val = (custom_id, game_consume_id, person_num, game_time, consume_time)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        return self.cursor.rowcount

    
    def insert_game_comsume(self, consume_start_time, consume_time, game_group_id, player_group_id):
        sql = 'INSERT INTO game_comsume (time, game_time, game_group, player_group) VALUES (%s, %s, %s, %s)'
        val = (consume_start_time, consume_time, game_group_id, player_group_id)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        return self.cursor.rowcount

    
    def insert_game_group(self, num, player_num, game_lever, member_info):
        sql = 'INSERT INTO game_group (num, player_num, game_lever, member_info) VALUES (%s, %s, %s, %s)'
        val = (num, player_num, game_lever, member_info)
        result = self.cursor.execute(sql, val)
        print('result', result)
        self.mydb.commit()
        return self.cursor.rowcount

    
    def insert_player_group(self, player_num, player_info):
        sql = 'INSERT INTO player_group (player_num, player_info) VALUES (%s, %s)'
        val = (player_num, player_info)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        return self.cursor.rowcount

    
    def select_last_insert_id(self):
        sql = 'select LAST_INSERT_ID()'
        num = self.cursor.execute(sql)
        result = self.cursor.fetchone()
        return result[0]

    
    def insert_part_game_over(self, game_name, game_lever, player_group, time_use, pass_time, game_scode):
        sql = 'INSERT INTO part_game_over (game_name, game_lever, player_group, time_use, pass_time, game_scode) VALUES (%s, %s, %s, %s, %s, %s)'
        val = (game_name, game_lever, player_group, time_use, pass_time, game_scode)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        return self.cursor.rowcount

    
    def insert_game_player_group(self, game_group, game_lever, time_use, pass_time, player_group, game_scode):
        sql = 'INSERT INTO game_player_group (game_group, game_lever, time_use, pass_time, player_group, scode) VALUES (%s, %s, %s, %s, %s, %s)'
        val = (game_group, game_lever, time_use, pass_time, player_group, game_scode)
        self.cursor.execute(sql, val)
        self.mydb.commit()
        return self.cursor.rowcount

    
    def search_game_result(self):
        sql = 'select gp.game_lever, gp.time_use, gp.pass_time,         gp.scode, p.player_info, g.member_info, gp.player_group from game_player_group gp, player_group p, game_group g where gp.game_group = g.game_group_id and gp.player_group = p.player_group_id ORDER BY gp.scode DESC'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.mydb.commit()
        return result

    
    def search_game_result2(self, num = (1,)):
        sql = 'select gp.scode, p.player_info from game_player_group gp, player_group p where gp.player_group = p.player_group_id ORDER BY gp.scode DESC limit ' + str(num)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.mydb.commit()
        return result

    
    def search_game_result_order_by_time(self, num = (1,)):
        sql = 'select gp.scode, gp.pass_time, p.player_info from game_player_group gp, player_group p where gp.player_group = p.player_group_id ORDER BY gp.pass_time DESC limit ' + str(num)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.mydb.commit()
        return result

    
    def __init__(self, ip_address):
        self.table_name = self.connect_db(ip_address)

    
    def close_db(self):
        self.cursor.close()
        self.mydb.cmd_quit()


