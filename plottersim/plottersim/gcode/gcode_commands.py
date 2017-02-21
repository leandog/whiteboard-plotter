from pydispatch import dispatcher
from plottersim.gcode.bbox import BBox
from plottersim.gcode.layer import Layer
from plottersim.gcode.segment import Segment

OK = 'ok'

def G00(parser, model, args):
    return G0_G1(parser, model, args, 'G0')

def G01(parser, model, args):
    return G0_G1(parser, model, args, 'G0')

def G02(parser, model, args):
    return G0_G1(parser, model, args, 'G0')

def G03(parser, model, args):
    return G0_G1(parser, model, args, 'G0')

def G0(parser, model, args):
    # G0: Rapid move
    # same as a controlled move for us (& reprap FW)
    return G0_G1(parser, model, args, 'G0')

def G1(parser, model, args):
    # G1: Controlled move
    return G0_G1(parser, model, args, 'G1')

def G0_G1(parser, model, args, type):
    args = _parse_args(args)
    # G0/G1: Rapid/Controlled move
    # clone previous coords
    coords = dict(model.relative)
    # update changed coords
    for axis in args.keys():
        if axis in coords:
            if model.is_relative:
                coords[axis] += args[axis]
            else:
                coords[axis] = args[axis]
        else:
            parser.warn("Unknown axis '%s'"%axis)
    # build segment
    absolute = {
        "X": model.offset["X"] + coords["X"],
        "Y": model.offset["Y"] + coords["Y"],
        "Z": model.offset["Z"] + coords["Z"],
        "F": coords["F"],   # no feedrate offset
        "E": model.offset["E"] + coords["E"]
    }
    seg = Segment(
        type,
        absolute,
        parser.line_number,
        parser.line)

    previous_segment = model.segments[-1] if len(model.segments) > 0 else None
    model.add_segment(seg)
    dispatcher.send(signal='SEGMENT_ADDED', sender=parser, previous_segment=previous_segment, current_segment=seg)

    # update model coords
    model.relative = coords

    return OK

def G20(parser, model, args):
    # G20: Set Units to Inches
    parser.error("Unsupported & incompatible: G20: Set Units to Inches")
    return OK

def G21(parser, model, args):
    # G21: Set Units to Millimeters
    # Default, nothing to do
    return OK
    
def G28(parser, model, args):
    # G28: Move to Origin
    parser.warn("G28 unimplemented")
    return OK

def G90(parser, model, args):
    # G90: Set to Absolute Positioning
    model.set_relative(False)
    return OK

def G91(parser, model, args):
    # G91: Set to Relative Positioning
    model.set_relative(True)
    return OK
    
def G92(parser, model, args):
    args = _parse_args(args)
    # G92: Set Position
    # this changes the current coords, without moving, so do not generate a segment
    
    # no axes mentioned == all axes to 0
    if not len(args.keys()):
        args = {"X":0.0, "Y":0.0, "Z":0.0, "E":0.0}
    # update specified axes
    for axis in args.keys():
        if axis in model.offset:
            # transfer value from relative to offset
            model.offset[axis] += model.relative[axis] - args[axis]
            model.relative[axis] = args[axis]
        else:
            parser.warn("Unknown axis '%s'"%axis)

    return OK

def M105(parser, model, args):
    # M105: Get extruder temperature
    return OK + ' T:0 B:0'

def _parse_args(args):
    dic = {}
    if args:
        bits = args.split()
        for bit in bits:
            letter = bit[0]
            coord = float(bit[1:])
            dic[letter] = coord
    return dic

