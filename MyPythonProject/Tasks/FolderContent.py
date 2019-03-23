# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import argparse
import locale
import os
from collections import Counter
from itertools import chain, tee
from operator import itemgetter
from pathlib import PureWindowsPath

from Applications.shared import TemplatingEnvironment, count_justify, format_collection

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

that_file = PureWindowsPath(os.path.abspath(__file__))

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "french")


# ==========
# Functions.
# ==========
def byextension(arg):
    """

    :param arg:
    :return:
    """
    return arg.suffix


def byname(arg):
    """

    :param arg:
    :return:
    """
    return arg.stem


def byparents(arg):
    """

    :param arg:
    :return:
    """
    return str(arg.parents[0])


def rjustify(arg, char=" ", length=5):
    """

    :param arg:
    :param char:
    :param length:
    :return:
    """
    return "{0:{1}>{2}d}".format(arg, char, length)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("path")
arguments = parser.parse_args()

# ==========
# Variables.
# ==========
dirs, empty_dirs = [], []

# =========
# Template.
# =========
template = TemplatingEnvironment(path=that_file.parents[0] / "Templates", keep_trailing_newline=False)
template.set_environment(filters={"rjustify": rjustify})
template.set_template(template="T01")

# ===============
# Main algorithm.
# ===============
for root, directories, files in os.walk(str(PureWindowsPath(arguments.path))):
    dirs.extend(PureWindowsPath(root) / PureWindowsPath(file) for file in files)
    if not any([directories, files]):
        empty_dirs.extend(PureWindowsPath(root) / PureWindowsPath(directory) for directory in directories)
dirs = sorted(sorted(sorted(dirs, key=byname), key=byextension), key=byparents)
it1, it2 = tee(dirs)
extensions = filter(None, sorted([(key[1:], value) for key, value in count_justify(*Counter(file.suffix for file in it1).items())], key=itemgetter(0)))
directories = filter(None, sorted([(str(key), value) for key, value in count_justify(*Counter(file.parents[0] for file in it2).items())], key=itemgetter(0)))
print(getattr(template, "template").render(root=arguments.path, dirs=dirs, extensions=extensions, directories=directories, empty_directories=empty_dirs))
