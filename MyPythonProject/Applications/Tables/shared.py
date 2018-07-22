# -*- coding: utf-8 -*-
__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ========
# Classes.
# ========
class ToBoolean(object):
    def __init__(self, arg):
        self.bool = False
        if arg.lower() == "y":
            self.bool = True
        if arg.lower() == "yes":
            self.bool = True


# ==========
# Functions.
# ==========
def adapt_booleanvalue(boolobj):
    """
    Adapt a python boolean value to an integer value accepted by sqlite3 module.
    :param boolobj: object created from `ToBoolean` class.
    """
    d = {False: 0, True: 1}
    return d[boolobj.bool]


def convert_tobooleanvalue(i):
    """
    Convert an integer value to a python boolean value.
    :param i: integer value.
    """
    return bool(int(i))
