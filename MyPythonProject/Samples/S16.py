# -*- coding: utf-8 -*-
from Applications.shared import filesinfolder
from Applications.AudioCD.shared import getmetadata

__author__ = 'Xavier ROSSET'


for file in filesinfolder(folder=r"C:\Users\Xavier\Music\groove\Osbourne, Ozzy"):
    print("# ---------- #")
    a, b, c, d = getmetadata(file)
    if b:
        for k in sorted(c):
            print("{0}: {1}".format(k.upper(), c[k]))
        print(len(c))

