# -*- coding: utf-8 -*-
from timeit import timeit

__author__ = "Xavier ROSSET"

imp = """\
import os
from Applications.shared import filesinfolder
"""
print(timeit(stmt='sorted(sorted(filesinfolder("jpg", folder=r"G:\Vidéos\Samsung S5")), key=lambda i: os.path.splitext(i)[1][1:])', setup=imp, number=100000))

imp = """\
from Images.CollectionLocal import images
"""
print(timeit(stmt='list(images())', setup=imp, number=50))
print(timeit(stmt='sorted(images())', setup=imp, number=50))

imp = """\
from Applications.shared import MUSIC
from Applications.AudioCD.shared import audiofilesinfolder
"""
print(timeit(stmt='audiofilesinfolder("flac", "m4a", folder=MUSIC)', setup=imp, number=100000))

imp = """\
import os
from Applications.AudioCD.shared import AudioFilesList
"""
print(timeit(stmt='AudioFilesList(folder=os.path.normpath(r"F:\S"), excluded=["recycle", "\$recycle"])', setup=imp, number=10))
