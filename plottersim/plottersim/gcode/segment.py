class Segment:

    def __init__(self, type, coords, lineNb, line):
        self.type = type
        self.coords = coords
        self.lineNb = lineNb
        self.line = line
        self.style = None
        self.layerIdx = None
        self.distance = None
        self.extrudate = None

    def __str__(self):
        return "<Segment: type=%s, lineNb=%d, style=%s, layerIdx=%d, distance=%f, extrudate=%f>"%(self.type, self.lineNb, self.style, self.layerIdx, self.distance, self.extrudate)
