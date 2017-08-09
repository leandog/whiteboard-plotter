#!/usr/bin/env python

import os
import time
import tty
import termios
import sys
import signal
import logging
from pydispatch import dispatcher
import curses
import gcode_sender

server = None

def signal_handler(signal, frame):
    if server:
        server.stop()
    sys.exit(0)

def exit_on_ctrl_c():
    signal.signal(signal.SIGINT, signal_handler)

def main():
    exit_on_ctrl_c()

    server = gcode_sender.GcodeSender()
    server.start()

    dispatcher.send(signal='HOME', sender=server)

    x,y = 1000.0,200.0

    while True:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        k = None
        new_x,new_y = x,y
        try:
            tty.setraw(sys.stdin.fileno())
            k = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if k=="k":
            print("up")
            new_y -= 10
        elif k=="j":
            print("down")
            new_y += 10
        elif k=="l":
            print("right")
            new_x += 10
        elif k=="h":
            print("left")
            new_x -= 10
        elif k=="q":
            print("penup")
            dispatcher.send(signal='PEN_LIFT', sender=server)
        elif k=="a":
            print("pendown")
            dispatcher.send(signal='PEN_DROP', sender=server)

        if x != new_x or y != new_y:
            dispatcher.send(signal='MOVE_TO_POINT', sender=server, x=new_x, y=new_y, speed=9600.0)
            x,y = new_x, new_y
        #time.sleep(100)

if __name__ == '__main__':
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
    }
    log_level_name = os.environ.get('GSV_LOG', 'INFO')
    logging.basicConfig(level=log_levels[log_level_name])
    logging.getLogger().setLevel(log_levels[log_level_name])
    logger = logging.getLogger(__name__)
    logger.debug('gcodeserver log level is {}'.format(log_level_name))
    main()
