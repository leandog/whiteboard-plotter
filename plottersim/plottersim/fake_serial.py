import re
import os
import time
import subprocess


def create_fake_serial_ports():
    with open('socat.tmp', 'w+') as output_file:
        proc = subprocess.Popen(['socat', '-d', '-d', 'pty,raw,echo=0', 'pty,raw,echo=0'], stderr=output_file)

    time.sleep(1)

    with open('socat.tmp', 'r') as read_output_file:
        master = None
        slave = None
        output = read_output_file.read()
        split_output = output.splitlines()
        for line in split_output:
            match = re.search(' E ', line)
            if match:
                print(line)

            match = re.search('(?<=N PTY is ).*', line)
            if match:
                if not master:
                    master = match.group()
                    continue
                elif not slave:
                    slave = match.group()
                    continue

    os.remove('socat.tmp')
    return (master, slave)
