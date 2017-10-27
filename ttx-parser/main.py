#!/usr/bin/env python

import xml.etree.ElementTree as ElementTree
import pprint

tree = ElementTree.parse("./Padauk.ttx")
root = tree.getroot()

font = {}
for glyph in root.findall(".//TTGlyph"):
    contours = []
    for contour in glyph.findall('./contour'):
        points = [(pt.get('x'),pt.get('y')) for pt in contour.findall('./pt')]
        contours.append(points)

    letter = glyph.get('name')
    font[letter] = contours

pprint.pprint(font)
