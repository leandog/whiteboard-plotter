class BBox(object):
    
    def __init__(self, coords):
        self.xmin = self.xmax = coords["X"]
        self.ymin = self.ymax = coords["Y"]
        self.zmin = self.zmax = coords["Z"]
        
    def dx(self):
        return self.xmax - self.xmin
    
    def dy(self):
        return self.ymax - self.ymin
    
    def dz(self):
        return self.zmax - self.zmin
        
    def cx(self):
        return (self.xmax + self.xmin)/2
    
    def cy(self):
        return (self.ymax + self.ymin)/2
    
    def cz(self):
        return (self.zmax + self.zmin)/2
    
    def extend(self, coords):
        self.xmin = min(self.xmin, coords["X"])
        self.xmax = max(self.xmax, coords["X"])
        self.ymin = min(self.ymin, coords["Y"])
        self.ymax = max(self.ymax, coords["Y"])
        self.zmin = min(self.zmin, coords["Z"])
        self.zmax = max(self.zmax, coords["Z"])
        
    def __str__(self):
        return "<BBox: xmin={},xmax={},ymin={},ymax={},zmin={},zmax={}>".format(self.xmin,self.xmax,self.ymin,self.ymax,self.zmin,self.zmax)
