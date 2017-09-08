#!/usr/bin/env python

import os
import sys
import signal
import logging
from pydispatch import dispatcher
import gcode_sender
import zerorpc

server = None

def signal_handler(signal, frame):
    if server:
        server.stop()
    sys.exit(0)

def exit_on_ctrl_c():
    signal.signal(signal.SIGINT, signal_handler)

class RpcHandler(object):
    def __init__(self):
        self.lift = True

    def on_connect(self, data):
        dispatcher.send(signal='PEN_LIFT', sender=server)
        dispatcher.send(signal='HOME', sender=server)
        return "OK"

    def on_disconnect(self, data):
        dispatcher.send(signal='PEN_LIFT', sender=server)
        dispatcher.send(signal='HOME', sender=server)
        return "OK"

    def draw(self, draw_data):
        print(draw_data)

        x = draw_data['x'] * 1040
        y = draw_data['y'] * 800
        dispatcher.send(signal='MOVE_TO_POINT', sender=server, x=x, y=y, speed=9600.0)

        new_lift = draw_data['lift'] == 1
        if new_lift != self.lift:
            self.lift = new_lift
            if self.lift:
                dispatcher.send(signal='PEN_LIFT', sender=server)
            else:
                dispatcher.send(signal='PEN_DROP', sender=server)

        return "OK"

def main():
    exit_on_ctrl_c()

    server = gcode_sender.GcodeSender()
    server.start()

    s = zerorpc.Server(RpcHandler())
    s.bind("tcp://0.0.0.0:4242")
    s.run()

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
