# -*- coding: utf-8 -*-
import fnmatch

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"


# ==========
# Functions.
# ==========
def subset(iterable, *patterns):
    collection = list(iterable)
    for pattern in patterns:
        collection = fnmatch.filter(collection, pattern)
    return collection


# ==========
# Constants.
# ==========
SRC = r"/volume1/homes/Xavier/CloudStation/Vidéos"
DST = r"/volume1/video"
SCRIPTS = r"/volume1/scripts"
