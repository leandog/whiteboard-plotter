import os
import pty
import time
import math
import threading
import binascii

from plottersim.gcode.bbox import BBox
from plottersim.gcode.layer import Layer
from plottersim.gcode.segment import Segment
import plottersim.gcode.gcode_commands as gcode_commands


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
        self.master_pty, self.slave_pty = pty.openpty()
        print('listening at {}'.format(os.ttyname(self.slave_pty)))

        self._stop.clear()
        self.parsing_thread = threading.Thread(target=self.read_serial)
        self.parsing_thread.daemon = True
        self.parsing_thread.start()

    def read_serial(self):
        input_buffer = ''
        self.line_number = 0
        while True:
            new_bytes = os.read(self.master_pty, 1024)
            input_buffer += new_bytes.decode('utf-8')

            last_new_line = input_buffer.rfind('\n')
            processing = input_buffer[:last_new_line+1]
            input_buffer = input_buffer[last_new_line+1:]
            for line in processing.splitlines(True):
                self.line_number += 1
                self.line = line.rstrip()
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

        os.write(self.master_pty, (response + '\n').encode('utf-8'))
        
    def warn(self, msg):
        print("[WARN] Line {}: {} (Text:'{}')".format(self.line_number, msg, self.line))
        
    def error(self, msg):
        print("[ERROR] Line {}: {} (Text:'{}')".format(self.line_number, msg, self.line))
        raise Exception("[ERROR] Line {}: {} (Text:'{}')".format(self.line_number, msg, self.line))
        
    def classify_segments(self):
        # apply intelligence, to classify segments
        
        # start model at 0
        coords = {
            "X":0.0,
            "Y":0.0,
            "Z":0.0,
            "F":0.0,
            "E":0.0}
            
        # first layer at Z=0
        currentLayerIdx = 0
        currentLayerZ = 0
        
        for seg in self.model.segments:
            # default style is fly (move, no extrusion)
            style = "fly"
            
            # no horizontal movement, but extruder movement: retraction/refill
            if (
                (seg.coords["X"] == coords["X"]) and
                (seg.coords["Y"] == coords["Y"]) and
                (seg.coords["E"] != coords["E"]) ):
                    style = "retract" if (seg.coords["E"] < coords["E"]) else "restore"
            
            # some horizontal movement, and positive extruder movement: extrusion
            if (
                ( (seg.coords["X"] != coords["X"]) or (seg.coords["Y"] != coords["Y"]) ) and
                (seg.coords["E"] > coords["E"]) ):
                style = "extrude"
            
            # positive extruder movement in a different Z signals a layer change for this segment
            if (
                (seg.coords["E"] > coords["E"]) and
                (seg.coords["Z"] != currentLayerZ) ):
                currentLayerZ = seg.coords["Z"]
                currentLayerIdx += 1
            
            # set style and layer in segment
            seg.style = style
            seg.layerIdx = currentLayerIdx
            
            
            #print coords
            #print seg.coords
            #print "%s (%s  | %s)"%(style, str(seg.coords), seg.line)
            #print
            
            # execute segment
            coords = seg.coords
            
            
    def split_layers(self):
        # split segments into previously detected layers
        
        # start model at 0
        coords = {
            "X":0.0,
            "Y":0.0,
            "Z":0.0,
            "F":0.0,
            "E":0.0}
            
        # init layer store
        self.model.layers = []
        
        currentLayerIdx = -1
        
        # for all segments
        for seg in self.model.segments:
            # next layer
            if currentLayerIdx != seg.layerIdx:
                layer = Layer(coords["Z"])
                layer.start = coords
                self.model.layers.append(layer)
                currentLayerIdx = seg.layerIdx
            
            layer.segments.append(seg)
            
            # execute segment
            coords = seg.coords
        
        self.topLayer = len(self.model.layers)-1
        
    def calc_metrics(self):
        # init distances and extrudate
        self.model.distance = 0
        self.model.extrudate = 0
        
        # init model bbox
        self.model.bbox = None
        
        # extender helper
        def extend(bbox, coords):
            if bbox is None:
                return BBox(coords)
            else:
                bbox.extend(coords)
                return bbox
        
        # for all layers
        for layer in self.model.layers:
            # start at layer start
            coords = layer.start
            
            # init distances and extrudate
            layer.distance = 0
            layer.extrudate = 0
            
            # include start point
            self.model.bbox = extend(self.model.bbox, coords)
            
            # for all segments
            for seg in layer.segments:
                # calc XYZ distance
                d  = (seg.coords["X"]-coords["X"])**2
                d += (seg.coords["Y"]-coords["Y"])**2
                d += (seg.coords["Z"]-coords["Z"])**2
                seg.distance = math.sqrt(d)
                
                # calc extrudate
                seg.extrudate = (seg.coords["E"]-coords["E"])
                
                # accumulate layer metrics
                layer.distance += seg.distance
                layer.extrudate += seg.extrudate
                
                # execute segment
                coords = seg.coords
                
                # include end point
                extend(self.model.bbox, coords)
            
            # accumulate total metrics
            self.model.distance += layer.distance
            self.model.extrudate += layer.extrudate
        
    def post_process(self):
        self.classify_segments()
        self.split_layers()
        self.calc_metrics()
