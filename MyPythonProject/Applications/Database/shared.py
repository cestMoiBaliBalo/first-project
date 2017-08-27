# -*- coding: ISO-8859-1 -*-
from contextlib import contextmanager
import sqlite3

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class Boolean(object):

    def __init__(self, s):
        self.bool = False
        if s.upper() == "Y":
            self.bool = True


# ==========
# Functions.
# ==========
def adapt_boolean(b):
    d = {False: 0, True: 1}
    return d[b.bool]


def convert_boolean(i):
    d = {0: False, 1: True}
    return d[int(i)]
