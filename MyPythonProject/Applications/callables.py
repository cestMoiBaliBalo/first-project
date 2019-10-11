# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import fnmatch
from functools import partial, wraps
from pathlib import Path
from typing import Optional, Set, Union

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


# ===========
# Decorators.
# ===========
def filterfalse(func):
    @wraps(func)
    def wrapper(cwdir, *names):
        return set(str(Path(cwdir) / name) for name in names) - func(cwdir, *names)

    return wrapper


def filter_extensions(*extensions):
    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(*args):
            files = set()
            for extension in extensions:
                files = files | func(*args, extension=extension)
            return files

        return inner_wrapper

    return outer_wrapper


# =================
# Global functions.
# =================
def filter_extension(cwdir: Union[str, Path], *names: str, extension: Optional[str] = None) -> Set[str]:
    """
    :param cwdir:
    :param names:
    :param extension:
    :return:
    """
    files = set(names)  # type: Set[str]
    if extension:
        files = set(fnmatch.filter(names, f"*.{extension}"))
    return set(str(Path(cwdir) / file) for file in files)


filter_audiofiles = filter_extensions("ape", "dsf", "flac", "mp3", "m4a", "ogg")(filter_extension)
filter_losslessaudiofiles = filter_extensions("ape", "dsf", "flac")(filter_extension)
filter_portablesdocuments = partial(filter_extension, extension="pdf")
