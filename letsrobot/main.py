#!/usr/bin/env python

import os
import time
import pty
import serial
import zerorpc

master, slave = pty.openpty()
print(os.ttyname(slave))

client = zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")

command_map = {
        'l' : client.left,
        'r' : client.right,
        'u' : client.up,
        'd' : client.down,
        'lift' : client.pen_lift,
        'drop' : client.pen_drop,
        'center' : client.center,
        'home' : client.home,
}

while True:
    command_string = os.read(master, 1024).decode("utf-8")
    commands = command_string.splitlines()
    for command in commands:
        if command in command_map:
            print("executing command \"{}\"".format(command))
            command_map[command]()
        else:
            print("unknown command \"{}\"".format(command))

    time.sleep(1)



