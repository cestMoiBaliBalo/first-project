# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import fnmatch
from functools import partial, wraps
from pathlib import Path
from typing import Set

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ==========
# Functions.
# ==========
def filter_extension(cwdir, *names, extension=None):
    """
    Function that returns a set of paths filtered by any optional extension.
    """
    files = set(names)  # type: Set[str]
    if extension:
        files = set(fnmatch.filter(names, f"*.{extension}"))
    return set(Path(cwdir) / file for file in files)


# ==========
# Callables.
# ==========
def filter_extensions(*extensions):
    """
    Callable that returns a set of paths filtered by the extensions contained into
    the argument `extensions`.
    """
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
    """
    Decorator that returns the difference between two set of paths.
    The first set is built with the arguments received by the wrapped function.
    The second set is built with the decorated function.
    """
    @wraps(func)
    def wrapper(cwdir: Path, *names: str) -> Set[Path]:
        return set(Path(cwdir) / name for name in names) - func(cwdir, *names)

    return wrapper


def match_(func):
    """
    Callable that returns the result of a regular expression applied to any string argument.
    Only re.match or re.search are coherent as wrapped function.

    ''''''''''''''
    How to use it:
    ''''''''''''''
    1. filter(match_(regex.search), [arg1, arg2, arg3, ...]): removes items non compliant with the regular expression.

    """

    @wraps(func)
    def wrapper(arg):
        return func(arg)

    return wrapper


def group_(index: int = 1):
    """
    Callable factory.
    Make a callable that returns the matching group from a regular expression applied to any string argument.
    The matching group position is set with the `index` argument.
    Only re.match or re.search are coherent as wrapped function.

    ''''''''''''''
    How to use it:
    ''''''''''''''
    1. sorted([arg1, arg2, arg3, ...], key=group_(1)(regex.search))
    2. with an additional decorator that converts the matching group content to a decimal integer.
       def mycallable_(func):
           @wraps(func)
           def wrapper(arg):
               return int(func(arg)) > 100
           return wrapper
       filter(mycallable_(group_(1)(regex.search)), [arg1, arg2, arg3, ...]): removes items less than or equal to 100.

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


filter_audiofiles = filter_extensions("ape", "dsf", "flac", "m4a", "mp3", "ogg")
filter_losslessaudiofiles = filter_extensions("ape", "dsf", "flac")
filter_portabledocuments = partial(filter_extension, extension="pdf")
