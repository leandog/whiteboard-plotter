import time
import math

from plottersim.gcode.bbox import BBox
from plottersim.gcode.layer import Layer
from plottersim.gcode.segment import Segment
from plottersim.gcode.plotter_model import PlotterModel


class GcodeParser:
    
    def __init__(self):
        self.model = PlotterModel()
        
    def parse_file(self, path):
        # read the gcode file
        with open(path, 'r') as f:
            # init line counter
            self.lineNb = 0
            # for all lines
            for line in f:
                # inc line counter
                self.lineNb += 1
                # remove trailing linefeed
                self.line = line.rstrip()
                # parse a line
                self.parseLine()
            
        self.postProcess()
        return self.model
        
    def parseLine(self):
        # strip comments:
        bits = self.line.split(';',1)
        if (len(bits) > 1):
            comment = bits[1]
        
        # extract & clean command
        command = bits[0].strip()
        
        # TODO strip logical line number & checksum
        
        # code is fist word, then args
        comm = command.split(None, 1)
        code = comm[0] if (len(comm)>0) else None
        args = comm[1] if (len(comm)>1) else None
        
        if code:
            if hasattr(self, "parse_"+code):
                getattr(self, "parse_"+code)(args)
            else:
                self.warn("Unknown code '%s'"%code)
        
    def parseArgs(self, args):
        dic = {}
        if args:
            bits = args.split()
            for bit in bits:
                letter = bit[0]
                coord = float(bit[1:])
                dic[letter] = coord
        return dic

    def parse_G0(self, args):
        # G0: Rapid move
        # same as a controlled move for us (& reprap FW)
        self.G1(args, "G0")
        
    def parse_G1(self, args, type="G1"):
        # G1: Controlled move
        self.do_G1(self.parseArgs(args), type)
        
    def parse_G20(self, args):
        # G20: Set Units to Inches
        self.error("Unsupported & incompatible: G20: Set Units to Inches")
        
    def parse_G21(self, args):
        # G21: Set Units to Millimeters
        # Default, nothing to do
        pass
        
    def parse_G28(self, args):
        # G28: Move to Origin
        self.do_G28(self.parseArgs(args))
        
    def parse_G90(self, args):
        # G90: Set to Absolute Positioning
        self.model.setRelative(False)
        
    def parse_G91(self, args):
        # G91: Set to Relative Positioning
        self.model.setRelative(True)
        
    def parse_G92(self, args):
        # G92: Set Position
        self.do_G92(self.parseArgs(args))

    def do_G1(self, args, type):
        # G0/G1: Rapid/Controlled move
        # clone previous coords
        coords = dict(self.model.relative)
        # update changed coords
        for axis in args.keys():
            if axis in coords:
                if self.model.isRelative:
                    coords[axis] += args[axis]
                else:
                    coords[axis] = args[axis]
            else:
                self.warn("Unknown axis '%s'"%axis)
        # build segment
        absolute = {
            "X": self.model.offset["X"] + coords["X"],
            "Y": self.model.offset["Y"] + coords["Y"],
            "Z": self.model.offset["Z"] + coords["Z"],
            "F": coords["F"],   # no feedrate offset
            "E": self.model.offset["E"] + coords["E"]
        }
        seg = Segment(
            type,
            absolute,
            self.lineNb,
            self.line)
        self.model.addSegment(seg)
        # update model coords
        self.model.relative = coords
        
    def do_G28(self, args):
        # G28: Move to Origin
        self.warn("G28 unimplemented")
        
    def do_G92(self, args):
        # G92: Set Position
        # this changes the current coords, without moving, so do not generate a segment
        
        # no axes mentioned == all axes to 0
        if not len(args.keys()):
            args = {"X":0.0, "Y":0.0, "Z":0.0, "E":0.0}
        # update specified axes
        for axis in args.keys():
            if axis in self.model.offset:
                # transfer value from relative to offset
                self.model.offset[axis] += self.model.relative[axis] - args[axis]
                self.model.relative[axis] = args[axis]
            else:
                self.warn("Unknown axis '%s'"%axis)
        
    def warn(self, msg):
        print("[WARN] Line {}: {} (Text:'{}')".format(self.lineNb, msg, self.line))
        
    def error(self, msg):
        print("[ERROR] Line {}: {} (Text:'{}')".format(self.lineNb, msg, self.line))
        raise Exception("[ERROR] Line {}: {} (Text:'{}')".format(self.lineNb, msg, self.line))
        
    def classifySegments(self):
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
            
            
    def splitLayers(self):
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
        
    def calcMetrics(self):
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
        
    def postProcess(self):
        self.classifySegments()
        self.splitLayers()
        self.calcMetrics()
