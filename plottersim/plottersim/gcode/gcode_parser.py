from plottersim.gcode.gcode_model import GcodeModel


class GcodeParser:
    
    def __init__(self):
        self.model = GcodeModel(self)
        
    def parseFile(self, path):
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
            
        self.model.postProcess()
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
        self.model.do_G1(self.parseArgs(args), type)
        
    def parse_G20(self, args):
        # G20: Set Units to Inches
        self.error("Unsupported & incompatible: G20: Set Units to Inches")
        
    def parse_G21(self, args):
        # G21: Set Units to Millimeters
        # Default, nothing to do
        pass
        
    def parse_G28(self, args):
        # G28: Move to Origin
        self.model.do_G28(self.parseArgs(args))
        
    def parse_G90(self, args):
        # G90: Set to Absolute Positioning
        self.model.setRelative(False)
        
    def parse_G91(self, args):
        # G91: Set to Relative Positioning
        self.model.setRelative(True)
        
    def parse_G92(self, args):
        # G92: Set Position
        self.model.do_G92(self.parseArgs(args))
        
    def warn(self, msg):
        print("[WARN] Line {}: {} (Text:'{}')".format(self.lineNb, msg, self.line))
        
    def error(self, msg):
        print("[ERROR] Line {}: {} (Text:'{}')".format(self.lineNb, msg, self.line))
        raise Exception("[ERROR] Line {}: {} (Text:'{}')".format(self.lineNb, msg, self.line))

