import math

from plottersim.gcode.bbox import BBox
from plottersim.gcode.layer import Layer
from plottersim.gcode.segment import Segment


class GcodeModel:
    
    def __init__(self, parser):
        # save parser for messages
        self.parser = parser
        # latest coordinates & extrusion relative to offset, feedrate
        self.relative = {
            "X":0.0,
            "Y":0.0,
            "Z":0.0,
            "F":0.0,
            "E":0.0}
        # offsets for relative coordinates and position reset (G92)
        self.offset = {
            "X":0.0,
            "Y":0.0,
            "Z":0.0,
            "E":0.0}
        # if true, args for move (G1) are given relatively (default: absolute)
        self.isRelative = False
        # the segments
        self.segments = []
        self.layers = None
        self.distance = None
        self.extrudate = None
        self.bbox = None
    
    def do_G1(self, args, type):
        # G0/G1: Rapid/Controlled move
        # clone previous coords
        coords = dict(self.relative)
        # update changed coords
        for axis in args.keys():
            if axis in coords:
                if self.isRelative:
                    coords[axis] += args[axis]
                else:
                    coords[axis] = args[axis]
            else:
                self.warn("Unknown axis '%s'"%axis)
        # build segment
        absolute = {
            "X": self.offset["X"] + coords["X"],
            "Y": self.offset["Y"] + coords["Y"],
            "Z": self.offset["Z"] + coords["Z"],
            "F": coords["F"],   # no feedrate offset
            "E": self.offset["E"] + coords["E"]
        }
        seg = Segment(
            type,
            absolute,
            self.parser.lineNb,
            self.parser.line)
        self.addSegment(seg)
        # update model coords
        self.relative = coords
        
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
            if axis in self.offset:
                # transfer value from relative to offset
                self.offset[axis] += self.relative[axis] - args[axis]
                self.relative[axis] = args[axis]
            else:
                self.warn("Unknown axis '%s'"%axis)

    def setRelative(self, isRelative):
        self.isRelative = isRelative
        
    def addSegment(self, segment):
        self.segments.append(segment)
        #print segment
        
    def warn(self, msg):
        self.parser.warn(msg)
        
    def error(self, msg):
        self.parser.error(msg)
        
        
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
        
        for seg in self.segments:
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
        self.layers = []
        
        currentLayerIdx = -1
        
        # for all segments
        for seg in self.segments:
            # next layer
            if currentLayerIdx != seg.layerIdx:
                layer = Layer(coords["Z"])
                layer.start = coords
                self.layers.append(layer)
                currentLayerIdx = seg.layerIdx
            
            layer.segments.append(seg)
            
            # execute segment
            coords = seg.coords
        
        self.topLayer = len(self.layers)-1
        
    def calcMetrics(self):
        # init distances and extrudate
        self.distance = 0
        self.extrudate = 0
        
        # init model bbox
        self.bbox = None
        
        # extender helper
        def extend(bbox, coords):
            if bbox is None:
                return BBox(coords)
            else:
                bbox.extend(coords)
                return bbox
        
        # for all layers
        for layer in self.layers:
            # start at layer start
            coords = layer.start
            
            # init distances and extrudate
            layer.distance = 0
            layer.extrudate = 0
            
            # include start point
            self.bbox = extend(self.bbox, coords)
            
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
                extend(self.bbox, coords)
            
            # accumulate total metrics
            self.distance += layer.distance
            self.extrudate += layer.extrudate
        
    def postProcess(self):
        self.classifySegments()
        self.splitLayers()
        self.calcMetrics()

    def __str__(self):
        return "<GcodeModel: len(segments)=%d, len(layers)=%d, distance=%f, extrudate=%f, bbox=%s>"%(len(self.segments), len(self.layers), self.distance, self.extrudate, self.bbox)
    
