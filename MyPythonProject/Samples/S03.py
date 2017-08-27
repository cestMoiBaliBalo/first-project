# -*- coding: utf-8 -*-
import os
from fnmatch import fnmatch
from itertools import groupby
from operator import itemgetter
import xml.etree.ElementTree as ET

__author__ = 'Xavier ROSSET'


def keyfunc(t):
    return t[0], t[1]


dirname = r"F:\I\INXS\1987 - Kick\1.Free Lossless Audio Codec"
d = []
for fil in os.listdir(dirname):
    if fnmatch(fil, "*.xml"):
        key = os.path.join(dirname, fil)
        tree = ET.parse(key)
        root = tree.getroot()
        tags = {item.tag: item.text for item in root.findall("ConvertedFile/IDTags/*")}
        if "artistsort" in tags:
            d.append((tags["artistsort"], tags["albumsort"], tags["titlesort"], tags["origyear"], tags["album"], tags["title"], tags["disc"], tags["track"], tags["upc"], tags["encodedby"], tags["disctotal"],
                      tags["tracktotal"]))
d = sorted(sorted(sorted(d, key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0))
for key, group in groupby(d, key=keyfunc):
    print(key)
    for item in group:
        print("{0}: {1} - {2} - {3}".format(itemgetter(2)(item), itemgetter(3)(item), itemgetter(4)(item), itemgetter(5)(item)))
