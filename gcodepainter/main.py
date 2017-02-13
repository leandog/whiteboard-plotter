#!/usr/bin/env python

import os
import sys
import signal
import logging
import gcodepainter


def exit_on_ctrl_c():
    signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    exit_on_ctrl_c()

    from gcodepainter.gcodepainter_app import GcodepainterApp
    GcodepainterApp().run()

if __name__ == '__main__':

    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
    }
    log_level_name = os.environ.get('GPT_LOG', 'INFO')
    logging.basicConfig(level=log_levels[log_level_name])
    logging.getLogger().setLevel(log_levels[log_level_name])
    logger = logging.getLogger(__name__)
    logger.debug('gcodepainter log level is {}'.format(log_level_name))
    main()
