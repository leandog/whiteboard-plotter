from pydispatch import dispatcher
import re
import time
import serial
import threading
from queue import Queue

PORT='/dev/ttyACM0'
SPEED=4800.0

class GcodeSender(object):

    PEN_LIFT_PULSE = 1500
    PEN_DROP_PULSE = 800

    def __init__(self, **kwargs):
        super(GcodeSender, self).__init__(**kwargs)
        self._stop = threading.Event()
        self.parsing_thread = None

        self.sent_commands = {}
        self.command_queue = Queue()
        self.line_number = 1
        self.plotter = None

        dispatcher.connect(self.on_pen_lift, signal='PEN_LIFT', sender=dispatcher.Any)
        dispatcher.connect(self.on_move_to_point, signal='MOVE_TO_POINT', sender=dispatcher.Any)
        dispatcher.connect(self.on_pen_drop, signal='PEN_DROP', sender=dispatcher.Any)
        dispatcher.connect(self.on_home, signal='HOME', sender=dispatcher.Any)
        dispatcher.connect(self.on_move_relative, signal='MOVE_RELATIVE', sender=dispatcher.Any)
        dispatcher.connect(self.on_gcode, signal='GCODE', sender=dispatcher.Any)

    def on_gcode(self, gcode):
        self.command_queue.put_nowait(gcode)

    def on_home(self):
        command = 'G28 X Y'
        self.command_queue.put_nowait(command)

    def on_move_relative(self, x, y, speed=SPEED):
        self.command_queue.put_nowait("G91")
        command = 'G1 X{0:.3f} Y{1:.3f} F{2:.1f}'.format(x,y,speed)
        self.command_queue.put_nowait(command)
        self.command_queue.put_nowait("G90")

    def on_move_to_point(self, x, y, speed=SPEED):
        self.command_queue.put_nowait("G90")
        command = 'G1 X{0:.3f} Y{1:.3f} F{2:.1f}'.format(x,y,speed)
        self.command_queue.put_nowait(command)

    def on_pen_drop(self):
        print("pen drop")
        self.command_queue.put_nowait("M400")
        self.command_queue.put_nowait("M340 P0 S{}".format(self.PEN_DROP_PULSE))
        self.command_queue.put_nowait("G4 S1")

    def on_pen_lift(self):
        print("pen lift")
        self.command_queue.put_nowait("M400")
        self.command_queue.put_nowait("M340 P0 S{}".format(self.PEN_LIFT_PULSE))
        self.command_queue.put_nowait("G4 P500")

    def start(self):
        self._stop.clear()
        self.parsing_thread = threading.Thread(target=self._start_processing)
        self.parsing_thread.daemon = True
        self.parsing_thread.start()

    def stop(self):
        if(self.plotter):
            self.plotter.close()
            self.plotter = None

    def __del__(self):
        self.stop_thread()
        self.stop()

    def _start_processing(self):
        self.command_queue.put_nowait('M110 N2')
        self.command_queue.put_nowait('G90')
        #self.command_queue.put_nowait('M205 T3 P145')
        self.plotter = serial.Serial(PORT, 115200, timeout=3)

        self._read_and_process_and_wait_for_ok(break_on_timeout=True)

        while True:
            if not self.command_queue.empty():
                command = self.command_queue.get_nowait()
                self.command_queue.task_done()
                self._send_line(command)

            self._read_and_process_and_wait_for_ok()

            time.sleep(0.01)

    def _send_line(self, line):
        command = 'N{} {} '.format(self.line_number, line)
        command = '{}*{}\n'.format(command, self._checksum(command))
        self.sent_commands[self.line_number] = command
        print("SEND: {}".format(command))
        self.line_number += 1
        self.plotter.write(command.encode('utf-8'))

    def _resend_line(self, line_number):
        if line_number not in self.sent_commands:
            raise Exception("requested resend of non-existant line number {}".format(line_number))

        command = self.sent_commands[line_number]
        print("RESEND: {}".format(command))
        self.plotter.write(command.encode('utf-8'))

    def _read_line(self):
        response = self.plotter.readline()
        print("READ: {}".format(response))
        return response.decode('utf-8')

    def _checksum(self, command):
        checksum = 0
        for char in command:
            byte_char = char.encode('utf-8')
            int_char = int.from_bytes(byte_char, 'big')
            checksum  = checksum ^ int_char
        return checksum

    def _parse_line_number_to_resend(self, response):
        line_number = None

        for regex in ["rs (\d+)", "Resend: (\d+)"]:
            match = re.search(regex, response)
            if not match:
                continue

            line_number = int(match.group())
            if not line_number:
                continue

            return line_number

        raise Exception("Could not parse line number from '{}'".format(response))

    def _read_and_process_and_wait_for_ok(self, break_on_timeout=False):
        response = self._read_line()

        if not response.strip() and break_on_timeout:
            return

        previous_line_number = self.line_number-1
        while not response.startswith('ok'):
            if response.startswith(('rs', 'Resend')):
                print('resend request: {}'.format(response))
                requested_line_number = self._parse_line_number_to_resend(response)
                self._resend_line(requested_line_number)
                response = self._read_line()
            elif response.startswith('!!'):
                raise Exception('printer fault')
            elif response.startswith('//'):
                print('comment: {}'.format(response))
                response = self._read_line()
            elif response.startswith('EPR:'):
                # dumping eeprom settings
                response = self._read_line()
            elif response.startswith('wait'):
                return
            elif response.startswith('start'):
                return
            else:
                print('unknown response: {}'.format(response))
                response = self._read_line()

    def stop_thread(self):
        self._stop.set()
        self.parsing_thread = None

