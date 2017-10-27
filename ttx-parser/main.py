#!/usr/bin/env python

import xml.etree.ElementTree as ElementTree
import pprint
import zerorpc

char = chr
try:
    char = unichr
except:
    pass

tree = ElementTree.parse("./Padauk.ttx")
root = tree.getroot()

HEIGHT = 875
SCALE = 0.1

font = {}
widths = {}
for glyph in root.findall(".//TTGlyph"):
    contours = []
    for contour in glyph.findall('./contour'):
        points = [(float(pt.get('x')) * SCALE,abs(HEIGHT - float(pt.get('y'))) * SCALE) for pt in contour.findall('./pt')]
        contours.append(points)

    letter_name = glyph.get('name')
    code = root.find(".//cmap//map[@name='{}']".format(letter_name)).get('code')
    if not code:
        break

    code_string = char(int(code, 16))

    font[code_string] = contours
    #font[letter_name] = contours
    try:
        widths[code_string] = float(glyph.get('xMax')) * SCALE
    except:
        pass

client = zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")

client.pen_lift()
client.home()

client.pen_lift()

y_offset = 200
x_offset = 0
margin = 20.0 * SCALE
for letter in "Test with space % $ # @":
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
