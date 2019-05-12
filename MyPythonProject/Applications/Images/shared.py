# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import json
import os
import sqlite3
from collections import OrderedDict
from contextlib import suppress
from pathlib import PurePath
from subprocess import PIPE, run
from tempfile import TemporaryFile
from typing import Tuple, Union

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

that_file = os.path.abspath(__file__)

# ==================
# Functions aliases.
# ==================
expandvars = os.path.expandvars


# =================
# Public interface.
# =================
def main(database: Union[str, PurePath], *paths: Union[str, PurePath], delete: bool = True) -> Tuple[int, int]:
    conn = sqlite3.connect(str(database))
    deleted = 0
    if delete:
        deleted = _delete_record(conn, *paths)
    collection = [("/".join(PurePath(file).parts[1:-1]), str(PurePath(file).name), datetimeoriginal) for file, datetimeoriginal in _get_metadata(*paths)]
    inserted = _insert_record(conn, *collection) - deleted
    conn.close()
    return deleted, inserted


# ===================
# Private interfaces.
# ===================
def _get_metadata(*paths: Union[str, PurePath]):
    collection = OrderedDict()
    args = [str(PurePath(expandvars("%_RESOURCES%")) / "exiftool.exe"),
            "-r",
            "-d",
            "%Y%m%d%H%M%S",
            "-j",
            "-charset",
            "Latin1",
            "-DateTimeOriginal",
            "-fileOrder",
            "DateTimeOriginal",
            "-ext",
            "jpg"]
    with TemporaryFile(mode="r+", encoding="UTF_8") as stream:
        args.extend(sorted(map(str, paths)))
        process = run(args, stdout=stream, stderr=PIPE, universal_newlines=True)
        if not process.returncode:
            stream.seek(0)
            for item in json.load(stream):
                with suppress(KeyError):
                    key = item["SourceFile"]
                    value = int(str(item["DateTimeOriginal"])[:8])
                    collection[key] = value
    for item in collection.items():
        yield item


def _delete_record(db_connector, *args: Union[str, PurePath]) -> int:
    with db_connector:
        db_connector.executemany("DELETE FROM images WHERE parent=?", [("/".join(path.parts[1:]),) for path in map(PurePath, args)])
    return db_connector.total_changes


def _insert_record(db_connector, *args: Tuple[str, str, int]) -> int:
    with db_connector:
        db_connector.executemany("INSERT INTO images (parent, name, datetimeoriginal) VALUES(?, ?, ?)", args)
    return db_connector.total_changes


# =============================
# Script if module run as main.
# =============================
if __name__ == "__main__":
    import argparse
    import operator
    from Applications.parsers import database_parser

    parser = argparse.ArgumentParser(parents=[database_parser])
    parser.add_argument("path", nargs="+")
    parser.add_argument("--dont_delete", action="store_true")
    arguments = parser.parse_args()
    _deleted, _inserted = main(arguments.db, *arguments.path, delete=operator.not_(arguments.dont_delete))
    print(_deleted)
    print(_inserted)
