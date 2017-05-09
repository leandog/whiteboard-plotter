#!/usr/bin/env python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("gcode_file", help="the gcode file to transform")
parser.add_argument("output_file", help="the gcode file to transform")
parser.add_argument("pen_drop_pulse", type=int, help="pulse to drop pen (500-2500)")
parser.add_argument("pen_lift_pulse", type=int, help="pulse to lift pen (500-2500)")
args = parser.parse_args()

with open(args.gcode_file, 'r') as input_file:
    with open(args.output_file, 'w') as output_file:
        for line in input_file:
            output_file.write(line)
            if line.startswith("G1 Z2.000"):
                output_file.write("M400\n")
                output_file.write("M340 P0 S{}\n".format(args.pen_lift_pulse))
                output_file.write("G4 P500\n")
            elif line.startswith("G1 Z1.000"):
                output_file.write("M400\n")
                output_file.write("M340 P0 S{}\n".format(args.pen_drop_pulse))
                output_file.write("G4 S1\n")

        output_file.write("M340 P0 S{}\n".format(args.pen_lift_pulse))
        output_file.write("G4 P500\n")
        output_file.write("G28 X Y\n")
