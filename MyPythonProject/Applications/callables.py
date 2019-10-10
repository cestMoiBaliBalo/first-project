# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import fnmatch
from itertools import chain
from pathlib import Path
from typing import List, Optional, Set, Union

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


def filter_byextension(cwdir: Union[str, Path], *names: str, extensions: Optional[List[str]] = None) -> Set[str]:
    """
    :param cwdir:
    :param names:
    :param extensions:
    :return:
    """
    files = set()  # type: Set[str]
    if extensions:
        files = set(names) - set(chain.from_iterable(fnmatch.filter(names, f"*.{_extension}") for _extension in extensions))
    return set(str(Path(cwdir) / file) for file in files)


def filter_portabledocuments(cwdir: Union[str, Path], *names: str) -> Set[str]:
    """

    :param cwdir:
    :param names:
    :return:
    """
    files = set(names) - set(fnmatch.filter(names, "*.pdf"))  # type: Set[str]
    return set(str(Path(cwdir) / file) for file in files)


def filter_losslessaudiofiles(cwdir: Union[str, Path], *names: str) -> Set[str]:
    """

    :param cwdir:
    :param names:
    :return:
    """
    ape = fnmatch.filter(names, "*.ape")
    flac = fnmatch.filter(names, "*.flac")
    files = set(names) - (set(ape) | set(flac))  # type: Set[str]
    return set(str(Path(cwdir) / file) for file in files)


def filter_audiofiles(cwdir: Union[str, Path], *names: str) -> Set[str]:
    """

    :param cwdir:
    :param names:
    :return:
    """
    ape = fnmatch.filter(names, "*.ape")
    dsf = fnmatch.filter(names, "*.dsf")
    flac = fnmatch.filter(names, "*.flac")
    mp3 = fnmatch.filter(names, "*.mp3")
    m4a = fnmatch.filter(names, "*.m4a")
    ogg = fnmatch.filter(names, "*.ogg")
    files = set(names) - (set(ape) | set(dsf) | set(flac) | set(mp3) | set(m4a) | set(ogg))  # type: Set[str]
    return set(str(Path(cwdir) / file) for file in files)
