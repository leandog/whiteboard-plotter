import os
import pty
import time
import math
import threading
import serial
import binascii

from plottersim.gcode.segment import Segment
import plottersim.gcode.gcode_commands as gcode_commands
import plottersim.fake_serial as fake_serial


class GcodeParser:
    
    def __init__(self, model):
        self.model = model

        self._stop = threading.Event()
        self.parsing_thread = None

    def __del__(self):
        self.stop_parsing()

    def stop_parsing(self):
        self._stop.set()
        self.parsing_thread = None

    def start_reading_serial(self):
        (master,slave)= fake_serial.create_fake_serial_ports()
        print('listening at {}'.format(slave))
        self.plotter = serial.Serial(master, 115200, timeout=1)

        self._stop.clear()
        self.parsing_thread = threading.Thread(target=self.read_serial)
        self.parsing_thread.daemon = True
        self.parsing_thread.start()

    def read_serial(self):
        input_buffer = ''
        self.line_number = 0

        while True:
            if self.line_number == 0:
                self.plotter.write("start\n".encode('utf-8'))

            response = self.plotter.readline()
            response = response.decode('utf-8').strip()

            if len(response):
                self.line = response
                self.line_number += 1
                self.parse_line()

    def parse_file_async(self, path):
        self._stop.clear()
        self._update.clear()
        self.parsing_thread = threading.Thread(target=self.parse_file, args=[path])
        self.parsing_thread.daemon = True
        self.parsing_thread.start()
        
    def parse_file(self, path):
        # read the gcode file
        with open(path, 'r') as f:
            # init line counter
            self.line_number = 0
            # for all lines
            for line in f:
                # inc line counter
                self.line_number += 1
                # remove trailing linefeed
                self.line = line.rstrip()
                # parse a line
                self.parse_line()
                time.sleep(0.01)
            
        self.post_process()

    def checksum(self, command):
        checksum = 0
        for char in command:
            byte_char = char.encode('utf-8')
            int_char = int.from_bytes(byte_char, 'big')
            checksum  = checksum ^ int_char
        return checksum

    def parse_line(self):
        # strip comments:
        bits = self.line.split(';',1)
        if (len(bits) > 1):
            comment = bits[1]
        
        # extract & clean command
        command = bits[0].strip()
        
        checksum_index = command.rfind('*')
        if checksum_index > 0:
            checksum = command[checksum_index+1:]
            command = command[:checksum_index]
            print('checksum: {}, command: {}'.format(checksum, command))
            print('calculated checksum: {}'.format(self.checksum(command)))
        
        # code is fist word, then args
        code = None
        args = None

        if command[:1] == 'N':
            comm = command.split(None, 2)
            print(comm)
            code = comm[1] if (len(comm)>1) else None
            args = comm[2] if (len(comm)>2) else None
        else:
            comm = command.split(None, 1)
            print(comm)
            code = comm[0] if (len(comm)>0) else None
            args = comm[1] if (len(comm)>1) else None

        response = 'ok'
        if code and hasattr(gcode_commands, code):
            response = getattr(gcode_commands,code)(self,self.model,args)
        else:
            self.warn('Unknown code {}'.format(code))

        self.plotter.write((response + "\n").encode('utf-8'))
        
    def warn(self, msg):
        print("[WARN] Line {}: {} (Text:'{}')".format(self.line_number, msg, self.line))
        
    def error(self, msg):
        print("[ERROR] Line {}: {} (Text:'{}')".format(self.line_number, msg, self.line))
        raise Exception("[ERROR] Line {}: {} (Text:'{}')".format(self.line_number, msg, self.line))
