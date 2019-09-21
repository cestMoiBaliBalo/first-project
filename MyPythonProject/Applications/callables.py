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
def exclude_allbutportabledocuments(*files):
    """

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


def exclude_allbutlosslessaudiofiles(*files):
    """

    :param files:
    :return:
    """
    ape = fnmatch.filter(files, "*.ape")
    flac = fnmatch.filter(files, "*.flac")
    return set(files) - (set(ape) | set(flac))


def exclude_allbutaudiofiles(*files):
    """

    :param files:
    :return:
    """
    ape = fnmatch.filter(files, "*.ape")
    dsf = fnmatch.filter(files, "*.dsf")
    flac = fnmatch.filter(files, "*.flac")
    mp3 = fnmatch.filter(files, "*.mp3")
    m4a = fnmatch.filter(files, "*.m4a")
    ogg = fnmatch.filter(files, "*.ogg")
    return set(files) - (set(ape) | set(dsf) | set(flac) | set(mp3) | set(m4a) | set(ogg))
