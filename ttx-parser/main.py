#!/usr/bin/env python

import xml.etree.ElementTree as ElementTree
import pprint
import zerorpc

char = chr
try:
    char = unichr
except:
    pass


HEIGHT = 875
MM_PER_EM = 100
FONT = "cube"

fonts = {
        "amplitude": "amplitude.ttx",
        "bendable": "bendable.ttx",
        "blox": "Blox2.ttx",
        "consolas": "Consolas.ttx",
        "cube": "Cube.ttx",
        "dotty": "dotty.ttx",
        "homeoutline": "home sweet home outline.ttx",
        "home": "home sweet home.ttx",
        "flesh": "intheflesh____.ttx",
        "surprise": "surprise.ttx",
}

font_path = "./fonts/{}".format(fonts[FONT])
tree = ElementTree.parse(font_path)
root = tree.getroot()

font = {}
widths = {}

units_per_em = float(root.findall(".//head/unitsPerEm")[0].get("value"))
y_offset = abs(float(root.findall(".//head/yMin")[0].get("value")))
x_offset = abs(float(root.findall(".//head/xMin")[0].get("value")))

for glyph in root.findall(".//TTGlyph"):
    contours = []
    for contour in glyph.findall('./contour'):
        points = []
        for pt in contour.findall('./pt'):
            fixed_x = float(pt.get('x')) + x_offset
            fixed_y = float(pt.get('y')) + y_offset
            x = fixed_x / units_per_em * MM_PER_EM
            y = fixed_y / units_per_em * MM_PER_EM
            y = MM_PER_EM - y
            y = y + MM_PER_EM

            points.append((x,y))
        contours.append(points)

    letter_name = glyph.get('name')
    code = None
    try:
        first_map = root.findall(".//cmap_format_4")[0]
        maps = first_map.findall("./map[@name='{}']".format(letter_name))
        code = maps[0].get('code')
    except:
        pass

    if not code:
        print("Failed to find map for {}".format(letter_name))
        continue 

    if len(code) > 4:
        #print("Failed to find single-byte code for {}".format(letter_name))
        continue 

    code_string = str(char(int(code, 16)))

    font[code_string] = contours
    try:
        mtx = root.findall(".//mtx[@name='{}']".format(letter_name))[0]
        widths[code_string] = float(mtx.get('width')) / units_per_em * MM_PER_EM
    except:
        pass

client = zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")

client.pen_lift()
client.home()

client.pen_lift()

y_offset = 0
x_offset = 50
margin = 2.0
for letter in "Hello world":
    for contour in font[letter]:
        first_x, first_y = contour[0]
        client.move_to_point(first_x + x_offset, first_y + y_offset)
        client.pen_drop()

        for x,y in contour:
            client.move_to_point(x + x_offset, y + y_offset)

        client.move_to_point(first_x + x_offset, first_y + y_offset)
        client.pen_lift()

    x_offset += widths[letter]
    x_offset += margin

client.pen_lift()
client.home()
