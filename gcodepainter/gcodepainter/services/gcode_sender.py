from pydispatch import dispatcher
import time
import serial
import threading
from queue import Queue

PORT='/dev/ttys009'
#PORT='/dev/tty.usbmodem1461'
SPEED=4800.0

class GcodeSender(object):

    def __init__(self, **kwargs):
        super(GcodeSender, self).__init__(**kwargs)
        self._stop = threading.Event()
        self.parsing_thread = None

        self.command_queue = Queue()
        self.line_number = 1
        self.plotter = None

        dispatcher.connect(self.on_move_to_point, signal='MOVE_TO_POINT', sender=dispatcher.Any)

    def on_move_to_point(self, x, y):
        command = 'G1 X{0:.3f} Y{1:.3f} F{2:.1f}'.format(x,y,SPEED)
        self.command_queue.put_nowait(command)

    def start(self):
        self._stop.clear()
        self.parsing_thread = threading.Thread(target=self.start_processing)
        self.parsing_thread.daemon = True
        self.parsing_thread.start()

    def stop(self):
        if(self.plotter):
            self.plotter.close()
            self.plotter = None

    def __del__(self):
        self.stop_thread()
        self.stop()

    def start_processing(self):
        self.command_queue.put_nowait('M110 N2')
        self.command_queue.put_nowait('G90')
        self.plotter = serial.Serial(PORT, 115200, timeout=1)

        self._read_and_process_and_wait_for_ok(break_on_timeout=True)

        while True:
            while not self.command_queue.empty():
                command = self.command_queue.get_nowait()
                self.command_queue.task_done()
                self._send_line(command)
                self._read_and_process_and_wait_for_ok()

            time.sleep(0.5)

    def _send_line(self, line):
        command = 'N{} {} '.format(self.line_number, line)
        command = '{}*{}\n'.format(command, self._checksum(command))
        print("SEND: {}".format(command))
        self.line_number += 1
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

    def _read_and_process_and_wait_for_ok(self, break_on_timeout=False):
        response = self._read_line()

        if not response.strip() and break_on_timeout:
            return

        previous_line_number = self.line_number-1
        while not response.startswith('ok'):
            if response.startswith((f"rs {previous_line_number}", f"Resend:{previous_line_number}")):
                print('resend request: {}'.format(response))
                self.line_number = self.line_number-1
                self._send_line(command)
                response = self._read_line()
            elif response.startswith(('rs', 'Resend')):
                raise Exception('requested resend of some other line number: {}'.format(response))
            elif response.startswith('!!'):
                raise Exception('printer fault')
            elif response.startswith('//'):
                print('comment: {}'.format(response))
                response = self._read_line()
            elif response.startswith('wait'):
                response = self._read_line()
                time.sleep(0.5)
            elif response.startswith('start'):
                return
            else:
                print('unknown response: {}'.format(response))
                response = self._read_line()
                #raise Exception('unknown response: {}'.format(response))

    def stop_thread(self):
        self._stop.set()
        self.parsing_thread = None

