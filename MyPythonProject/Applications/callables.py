# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import fnmatch
import os

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

# ------------------
# Functions aliases.
# ------------------
basename, join = os.path.basename, os.path.join


# ----------
# Functions.
# ----------
def exclude_allbutportabledocuments(curdir, *files):
    """

    :param curdir:
    :param files:
    :return:
    """
    return set(files) - set(fnmatch.filter(files, "*.pdf"))


def exclude_pythonexecutablebytecode(curdir, *files):
    """

    :param curdir:
    :param files:
    :return:
    """
    if fnmatch.fnmatch(curdir, "*\\.idea*"):
        return set(files)
    return set(fnmatch.filter(files, "*.pyc"))


def exclude_allbutlosslessaudiofiles(curdir, *files):
    """

    :param curdir:
    :param files:
    :return:
    """
    ape = fnmatch.filter(files, "*.ape")
    flac = fnmatch.filter(files, "*.flac")
    return set(files) - (set(ape) | set(flac))

# def exclude_allbutimagefiles(curdir, *files):
#     """
#
#     :param curdir:
#     :param files:
#     :return:
#     """
#     return set(files) - set(fnmatch.filter(files, "*.jpg"))
#
#
# def somefunc3(curdir, *files):
#     """
#
#     :param curdir:
#     :param files:
#     :return:
#     """
#     pdf = fnmatch.filter(files, "*.pdf")
#     txt = fnmatch.filter(files, "*.txt")
#     return set(files) - (set(pdf) | set(txt))
#
#
# def exclude_allbutaudiofiles(curdir, *files):
#     """
#
#     :param curdir:
#     :param files:
#     :return:
#     """
#     if fnmatch.fnmatch(curdir, "*RECYCLE*"):
#         return set(files)
#     flac = fnmatch.filter(files, "*.flac")
#     mp3 = fnmatch.filter(files, "*.mp3")
#     m4a = fnmatch.filter(files, "*.m4a")
#     return set(files) - (set(flac) | set(mp3) | set(m4a))


# def somefunc5(curdir, *files):
#     """
#
#     :param curdir:
#     :param files:
#     :return:
#     """
#     if fnmatch.fnmatch(curdir, r"*\visual studio 2017\*"):
#         return set(files)
#     docx = fnmatch.filter(files, "*.docx")
#     json = fnmatch.filter(files, "*.json")
#     txt = fnmatch.filter(files, "*.txt")
#     yml = fnmatch.filter(files, "*.yml")
#     return set(files) - (set(docx) | set(json) | set(txt) | set(yml))
#
#
# def somefunc6(curdir, *files):
#     """
#
#     :param curdir:
#     :param files:
#     :return:
#     """
#     return set(map(basename, set(map(join, repeat(curdir), files)) - set(fnmatch.filter(map(join, repeat(curdir), files), r"*\springsteen*.flac"))))
#
#
# def somefunc7(curdir, *files):
#     """
#
#     :param curdir:
#     :param files:
#     :return:
#     """
#     kiss = set(fnmatch.filter(map(join, repeat(curdir), files), r"*\kiss*.flac")) | set(fnmatch.filter(map(join, repeat(curdir), files), r"*\kiss*.m4a")) | set(
#         fnmatch.filter(map(join, repeat(curdir), files), r"*\kiss*.mp3"))
#     springsteen = set(fnmatch.filter(map(join, repeat(curdir), files), r"*\springsteen*.flac"))
#     return set(map(basename, set(map(join, repeat(curdir), files)) - (kiss | springsteen)))
#
#
# def pdffiles(curdir, *files):
#     """
#
#     :param curdir:
#     :param files:
#     :return:
#     """
#     return set(fnmatch.filter(files, "*.pdf"))
