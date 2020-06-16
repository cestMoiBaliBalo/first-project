# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import csv
import os
from contextlib import suppress
from itertools import compress, groupby
from operator import itemgetter
from pathlib import Path
from typing import Any, Iterator, List, Mapping, Tuple, Iterable

from Applications.decorators import itemgetter_
from Applications.shared import CustomDialect, TemplatingEnvironment, UTF8, WRITE

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent


# ================
# Local functions.
# ================
@itemgetter_(2)
def get_parent(path: str) -> Path:
    return Path(path).parent


@itemgetter_(2)
def get_name(path: str) -> str:
    return Path(path).name


def break_(item: Tuple[str, ...]) -> Iterator[str]:
    item = iter(item)
    with suppress(StopIteration):
        nexti = next(item)
        yield str(Path(nexti).parent)
        yield Path(nexti).name
    while True:
        try:
            nexti = next(item)
            yield nexti
        except StopIteration:
            break


# ==============
# Local classes.
# ==============
class GetPath(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetPath, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        setattr(namespace, self.dest, Path(values))


# ================
# Local constants.
# ================
RESOURCES = Path(os.path.expandvars("%_RESOURCES%"))  # type: Path
TEMPLATES = {(_MYPARENT / "AudioCD" / "Templates", "T00a"): [0, 0, 1, 1],
             (_MYPARENT / "AudioCD" / "Templates", "T00b"): [0, 0, 1]}  # type: Mapping[Tuple[Path, str], List[int]]

# ================
# Parse arguments.
# ================
parser = argparse.ArgumentParser()
parser.add_argument("--collection", default=Path(os.path.expandvars("%TEMP%")) / "tmp1n53chv0" / "tmplpg2af5i", nargs="?", action=GetPath)
parser.add_argument("--encoding", default=UTF8, nargs="?")
arguments = parser.parse_args()

# ============
# Main script.
# ============
with open(arguments.collection, encoding=arguments.encoding, newline="") as fr:
    collection = csv.reader(fr, dialect=CustomDialect())  # type: Iterable[Any]
    collection = sorted(collection, key=get_name)
    collection = sorted(collection, key=get_parent)
    collection = sorted(collection, key=itemgetter(1))
    collection = sorted(collection, key=itemgetter(0))
    for key, group in groupby(collection, key=itemgetter(0)):
        environment = TemplatingEnvironment(key)
        for sub_key, sub_group in groupby(group, key=itemgetter(1)):
            with open(Path(os.path.expandvars("%TEMP%")) / "tmp1n53chv0" / f"batch{sub_key}.cmd", mode=WRITE, encoding="ISO-8859-1") as fw:
                files = [tuple(compress(item, TEMPLATES.get((Path(key), sub_key)))) for item in sub_group]  # type: Iterable[Any]
                files = [tuple(break_(file)) for file in files]
                files = groupby(files, key=itemgetter(0))
                fw.write(environment.get_template(sub_key).render(collection=files))
