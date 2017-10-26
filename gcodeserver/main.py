#!/usr/bin/env python

import os
import sys
import signal
import logging

import zerorpc
from pydispatch import dispatcher

import gcode_sender
import rpc_handler


gcode_server = None
rpc_server = None


def main():
    _exit_on_ctrl_c()

    _configure_logging()

    gcode_server = gcode_sender.GcodeSender()
    gcode_server.start()

    rpc_server = zerorpc.Server(rpc_handler.RpcHandler())
    rpc_server.bind("tcp://0.0.0.0:4242")
    rpc_server.run()

def _signal_handler(signal, frame):
    if gcode_server:
        gcode_server.stop()
    sys.exit(0)

def _exit_on_ctrl_c():
    signal.signal(signal.SIGINT, _signal_handler)

def _configure_logging():
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

if __name__ == '__main__':
    main()
