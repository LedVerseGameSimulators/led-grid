# uncompyle6 version 3.9.3
# Python bytecode version base 3.7 (3394)
# Decompiled from: Python 3.7.17 (default, Sep 20 2023, 11:59:52) 
# [GCC 12.2]
# Embedded file name: communication.py
import loguru, serial
from serial.tools import list_ports

class Communication:

    def __init__(self, com, bps, timeout):
        global Ret
        self.port = com
        self.bps = bps
        self.timeout = timeout
        self.read_date_buffer = []
        try:
            self.main_engine = None
            self.main_engine = serial.Serial((self.port), (self.bps), timeout=(self.timeout))
            self.Print_Name()
            if self.main_engine.is_open:
                Ret = True
        except Exception as e:
            try:
                print("---异常---：", e)
            finally:
                e = None
                del e

    def Print_Name(self):
        print(self.main_engine.name)
        print(self.main_engine.port)
        print(self.main_engine.baudrate)
        print(self.main_engine.bytesize)
        print(self.main_engine.parity)
        print(self.main_engine.stopbits)
        print(self.main_engine.timeout)
        print(self.main_engine.writeTimeout)
        print(self.main_engine.xonxoff)
        print(self.main_engine.rtscts)
        print(self.main_engine.dsrdtr)
        print(self.main_engine.interCharTimeout)

    def Open_Engine(self):
        self.main_engine.open()

    def Close_Engine(self):
        if self.main_engine is not None:
            self.main_engine.close()
            loguru.logger.info("close {} state {}", self.main_engine.name, self.main_engine.is_open)

    @staticmethod
    def Print_Used_Com():
        port_list = list(serial.tools.list_ports.comports())
        print(port_list)

    @staticmethod
    def get_com_list():
        return list(serial.tools.list_ports.comports())

    def Read_Size(self, size):
        return self.main_engine.read(size=size)

    def Read_Line(self):
        return self.main_engine.readline()

    def Send_data(self, data):
        self.main_engine.write(data)

    def Recive_data(self, way):
        while True:
            try:
                if self.main_engine.in_waiting:
                    if way == 0:
                        for i in range(self.main_engine.in_waiting):
                            data1 = self.Read_Size(1).hex()
                            data2 = int(data1, 16)
                            if data2 == "exit":
                                break
                            else:
                                print("收到数据十六进制：" + data1 + " 收到数据十进制：" + str(data2))

                    elif way == 1:
                        data = self.main_engine.read_all()
                        if data == "exit":
                            break
                        else:
                            print("接收ascii数据：", data)
            except Exception as e:
                try:
                    print("异常报错：", e)
                finally:
                    e = None
                    del e



# okay decompiling /games/climb/climb_source_code/led/communication.pyc
