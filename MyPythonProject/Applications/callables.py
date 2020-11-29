# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import fnmatch
from functools import partial, wraps
from pathlib import Path
from typing import Set

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# =================
# Global functions.
# =================
def filter_extension(cwdir, *names, extension=None):
    """
    :param cwdir:
    :param names:
    :param extension:
    :return:
    """
    files = set(names)  # type: Set[str]
    if extension:
        files = set(fnmatch.filter(names, f"*.{extension}"))
    return set(Path(cwdir) / file for file in files)


# ==========
# Callables.
# ==========
def filter_extensions(*extensions):
    @wraps(filter_extension)
    def wrapper(cwdir: Path, *names: str) -> Set[Path]:
        files = set()  # type: Set[Path]
        for extension in extensions:
            files = files | filter_extension(cwdir, *names, extension=extension)
        return files

    return wrapper


# ===========
# Decorators.
# ===========
def filterfalse_(func):
    @wraps(func)
    def wrapper(cwdir: Path, *names: str) -> Set[Path]:
        return set(Path(cwdir) / name for name in names) - func(cwdir, *names)

    return wrapper


def match_(func):
    """
    Creates a callable object returning the result of a regular expression.
    Only re.match and re.search are useful as the wrapped function.

    ''''''''''''''
    How to use it:
    ''''''''''''''
    1. filter(match_(regex.search), [arg1, arg2, arg3, ...]): removes items non compliant with the regular expression.

    :param func: wrapped function.
    :return: callable object.
    """

    @wraps(func)
    def wrapper(arg):
        return func(arg)

    return wrapper


def group_(index: int = 1):
    """
    Creates a callable object returning the regular expression matching group located at position "index" (base 1).
    Only re.match and re.search are useful as the wrapped function.

    ''''''''''''''
    How to use it:
    ''''''''''''''
    1. sorted([arg1, arg2, arg3, ...], key=group_(1)(regex.search))
    2. with an additional decorator aiming at converting the matching group to a base 10 integer number.
       def mycallable_(func):
           @wraps(func)
           def wrapper(arg):
               return int(func(arg)) > 100
           return wrapper
       filter(mycallable_(group_(1)(regex.search)), [arg1, arg2, arg3, ...]): removes items less than or equal to 100.

    :param index: regular expression matching group position (base 1).
    :return: callable object.
    """

    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(arg):
            match = func(arg)
            if match:
                return match.group(index)
            return arg

        return inner_wrapper

    return outer_wrapper


filter_audiofiles = filter_extensions("ape", "dsf", "flac", "mp3", "m4a", "ogg")
filter_losslessaudiofiles = filter_extensions("ape", "dsf", "flac")
filter_portabledocuments = partial(filter_extension, extension="pdf")
