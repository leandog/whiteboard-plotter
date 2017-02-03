class Layer:
    def __init__(self, Z):
        self.Z = Z
        self.segments = []
        self.distance = None
        self.extrudate = None
        
    def __str__(self):
        return "<Layer: Z=%f, len(segments)=%d, distance=%f, extrudate=%f>"%(self.Z, len(self.segments), self.distance, self.extrudate)
