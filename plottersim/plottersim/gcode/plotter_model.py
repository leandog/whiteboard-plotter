class PlotterModel:

    def __init__(self):

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
        self.is_relative = False
    
        # the segments
        self.segments = []
        self.layers = None
        self.distance = None
        self.extrudate = None
        self.bbox = None
        
    def set_relative(self, is_relative):
        self.is_relative = is_relative
        
    def add_segment(self, segment):
        self.segments.append(segment)
