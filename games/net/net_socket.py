# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: net_socket.py
import json, os, sys, threading
from socket import *
import time, loguru
from encryption import yanqian
from led import led_control
from model.setting import Setting

class NetSocket:

    def __init__(self, localaddr=('127_iter__iter_.1', 8080)):
        self.is_running = True
        self.udp_socket = None
        self.recvfromaddress = None
        self.localaddr = localaddr
        self.game_last_result = []

    def message_controller(self):
        conn = self.connet
        while self.is_running:
            if conn.poll():
                data = conn.recv()
                print(f"子进程{os.getpid()}, recv: {data}")
                conn.send(data.upper() + str(len(data)))

    def send(self, message):
        self.game_last_result = message
        message = json.dumps(message)
        if self.recvfromaddress:
            self.udp_socket.sendto(message.encode("utf-8"), self.recvfromaddress)

    def waiting(self, running_to_flag=0):
        tmp_time = 5
        while self.parent.game_record_rt.running_to_flag != running_to_flag and tmp_time > 0:
            time.sleep(0.1)
            tmp_time -= 0.1

        loguru.logger.debug(f"running_to_flag:{self.parent.game_record_rt.running_to_flag};timeleft:{tmp_time}")
        if tmp_time < 0:
            return False
        return True

    def stop_game(self, parent):
        if parent.game_record_rt.running_to_flag == 2:
            if parent.game_record_rt.running_to_obj:
                parent.game_record_rt.running_to_obj.customized_function()
            loguru.logger.debug("in result ui, waiting close it ")
            ret = self.waiting(running_to_flag=0)
            loguru.logger.debug("in result ui, end of waiting")
        else:
            if parent.game_record_rt.running_to_flag == 1:
                if parent.game_record_rt.game_time_left > 1:
                    parent.game_record_rt.running_to_obj.customized_function()
                    loguru.logger.debug("in game ui, game not over, waiting close it ")
                    ret = self.waiting(running_to_flag=0)
                    loguru.logger.debug("in game ui, game not over, end of waiting")
                else:
                    parent.game_record_rt.running_to_obj.customized_function()
                    loguru.logger.debug("in game ui, game over, waiting close it ")
                    ret = self.waiting(running_to_flag=2)
                    loguru.logger.debug("in game ui, game over, end")
                    if ret:
                        if parent.game_record_rt.running_to_obj:
                            parent.game_record_rt.running_to_obj.customized_function()
                        loguru.logger.debug("in result ui, game over, waiting close it ")
                        ret = self.waiting(running_to_flag=0)
                        loguru.logger.debug("in result ui, game over, end ")
            else:
                parent.game_record_rt.running_to_obj.customized_function()
                loguru.logger.debug("in countdown ui, waiting close it ")
                ret = self.waiting(running_to_flag=0)
                loguru.logger.debug("in countdown ui, end ")
        loguru.logger.info("net running_obj customized_function  ")
        return ret

    def socket_running(self, parent):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_socket = udp_socket
        localaddr = self.localaddr
        udp_socket.bind(localaddr)
        self.parent = parent
        while self.is_running:
            try:
                recv_data = udp_socket.recvfrom(1024)
                message = recv_data[0].decode("utf-8")
                dip = recv_data[1][0]
                dport = recv_data[1][1]
                self.recvfromaddress = recv_data[1]
                message = json.loads(message)
                command_head = message[0]
                replay_command_head = None
                replay_message = ["already start"]
                if command_head == "START":
                    replay_command_head = "STARTREPLY"
                    replay_message = "NO_AUTH"
                    if yanqian.yanqian():
                        loguru.logger.info("net start command")
                        ret = True
                        if parent.game_record_rt.running_to_obj:
                            if parent.game_record_rt.running_to_obj != parent:
                                parent.game_record_rt.game_result = 3
                                ret = self.stop_game(parent)
                                if ret:
                                    parent.game_record_rt.running_to_obj = parent
                        if ret:
                            game_type_idx = int(message[1].split("-")[0]) - 1
                            game_idx = int(message[1].split("-")[1]) - 1
                            player_nums = int(message[2])
                            game_level = int(message[3])
                            game_time = message[4]
                            player_name = message[5]
                            if 0 < game_level < 4:
                                if parent.is_game_num_exist(game_type_idx, game_idx):
                                    loguru.logger.info("net bft root.after new start game ")
                                    parent.root.after(0, parent.game_start_thread, player_nums, game_type_idx, game_idx, game_time, player_name, game_level)
                                    time.sleep(0.3)
                                    loguru.logger.info("net aft root.after new start game ")
                                elif parent.game_record_rt.game_state == Setting.GAME_NUMBER_ERROR:
                                    replay_message = "FAIL-GAMENUMBER"
                                else:
                                    if parent.game_record_rt.game_state == Setting.GAME_HW_ERROR:
                                        replay_message = "FAIL-HARDWARE"
                                    else:
                                        replay_message = "SUCCESSFULL"
                            else:
                                replay_message = "FAIL-DIFFICULTY"
                        else:
                            replay_message = "FAIL"
                    replay_message = [
                     replay_command_head, replay_message]
                else:
                    if command_head == "STOP":
                        replay_message = [
                         "STOPREPLY", "SUCCESSFULL"]
                        loguru.logger.info("net STOP command")
                        ret = True
                        if parent.game_record_rt.running_to_obj and parent.game_record_rt.running_to_obj != parent:
                            parent.game_record_rt.game_result = 3
                            ret = self.stop_game(parent)
                            if ret:
                                parent.game_record_rt.running_to_obj = parent
                        elif ret:
                            parent.finish_game_in_main_ui2()
                            replay_message = "SUCCESS"
                        else:
                            replay_message = "FAIL"
                        replay_message = ["STOPREPLY", replay_message]
                    else:
                        if command_head == "GETSTATUS":
                            if parent.game_record_rt.game_time_start > 0 and parent.game_record_rt.game_time_left > 1:
                                a = 1
                                replay_message = ["STATUSREPLY", "RUNNING", int(parent.game_record_rt.game_time_left)]
                            else:
                                replay_message = [
                                 "STATUSREPLY", "IDLE"]
                                serial_list_error = parent.game_idle is not None and parent.game_idle.is_alive() or led_control.init_com(parent.setting.list_com_info)
                                led_control.close_com()
                                if len(serial_list_error) > 0:
                                    replay_message = [
                                     "STATUSREPLY", "HARDWARE DISCONNECTED"]
                        else:
                            if command_head == "GETRANKING":
                                replay_message = [
                                 "RANKING"] + [parent.get_rangking()]
                            else:
                                if command_head == "GETGAMEDICT":
                                    replay_message = [
                                     "GAMEDICT"] + [parent.dict_all_game]
                                else:
                                    if command_head == "GET_CUR_PLAYER_RANKING":
                                        replay_message = [
                                         "PLAYER_RANKING"] + [parent.last_game_score] + [parent.last_player_ranking]
                                    else:
                                        if command_head == "clientclose":
                                            replay_message = [
                                             "clientclose"] + ["return"]
                                        replay_message = json.dumps(replay_message)
                                        udp_socket.sendto(replay_message.encode("utf-8"), recv_data[1])
            except:
                loguru.logger.info(sys.exc_info())
                replay_message = ["exception"]
                replay_message = json.dumps(replay_message)
                try:
                    udp_socket.sendto(replay_message.encode("utf-8"), recv_data[1])
                except:
                    pass

        udp_socket.close()

# okay decompiling /games/climb/climb_source_code/net/net_socket.pyc
