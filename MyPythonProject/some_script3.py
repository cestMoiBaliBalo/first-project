# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import fnmatch
import logging.config
import os
import timeit
from functools import partial
from itertools import repeat, chain
from typing import Iterable, List, Optional, Set

import yaml

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "Resources", "logging.yml"), encoding="UTF_8") as fp:
    logging.config.dictConfig(yaml.load(fp))


def find_files(directory: str, *, excluded=None) -> Iterable[str]:
    """
    Return a generator object yielding files stored in `directory`.
    :param directory: directory to walk through.
    :param excluded: callable returning a list composed of files to exclude as returned by os.listdir.
                     Callable input arguments must be:
                        :The root directory returned by os.walk.
                        :The list of files present into the root directory.
    :return: generator object.
    """
    collection = []
    if not excluded:
        collection.extend(map(os.path.join, repeat(root), files) for root, _, files in os.walk(directory) if files)
    else:
        for root, _, files in os.walk(directory):
            if files:
                files = set(files) - excluded(root, *files)
                if files:
                    collection.extend(map(os.path.join, repeat(root), files))
    for file in sorted(collection):
        yield file


def find_files2(directory: str, *, excluded=None) -> Iterable[str]:
    """
    Return a generator object yielding files stored in `directory`.
    :param directory: directory to walk through.
    :param excluded: callable returning a list composed of files to exclude as returned by os.listdir.
                     Callable input arguments must be:
                        :The root directory returned by os.walk.
                        :The list of files present into the root directory.
    :return: generator object.
    """
    collection = []
    for root, _, files in os.walk(directory):
        if files:
            if excluded:
                files = set(files) - excluded(root, *files)
                if files:
                    collection.extend(map(os.path.join, repeat(root), files))
            else:
                collection.extend(files)
    for file in sorted(collection):
        yield file


def exclude_allbut(curdir: str, *files: str, extensions: Optional[List[str]] = None) -> Set[str]:
    """
    :param curdir:
    :param files:
    :param extensions:
    :return:
    """
    if extensions:
        return set(files) - set(chain.from_iterable(fnmatch.filter(files, f"*.{extension}") for extension in extensions))
    return set()


t = timeit.Timer(stmt='find_files(r"F:\B\Black Sabbath", excluded=partial(exclude_allbut, extensions=["dsf", "flac"]))', globals=globals())
print(t.repeat())
t = timeit.Timer(stmt='find_files2(r"F:\B\Black Sabbath", excluded=partial(exclude_allbut, extensions=["dsf", "flac"]))', globals=globals())
print(t.repeat())
# for file in find_files(r"F:\B\Black Sabbath", excluded=partial(exclude_allbut, extensions=["dsf", "flac"])):
#     print(file)
