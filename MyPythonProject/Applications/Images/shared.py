# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import json
import os
from collections import OrderedDict
from contextlib import suppress
from pathlib import PurePath
from subprocess import PIPE, run
from tempfile import TemporaryFile
from typing import Dict, Iterable, Optional, Tuple, Union

import yaml

from ..Tables.shared import DatabaseConnection

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

that_file = PurePath(os.path.abspath(__file__))

# ==================
# Functions aliases.
# ==================
expandvars = os.path.expandvars


# =================
# Public interface.
# =================
def main(database: Union[str, PurePath], *paths: Union[str, PurePath], delete: bool = True) -> Tuple[int, int]:
    deleted, inserted = 0, 0
    with DatabaseConnection(str(database)) as conn:
        if delete:
            deleted = _delete_records(conn, *paths)
        collection = [("/".join(PurePath(file).parts[1:-1]), str(PurePath(file).name), datetimeoriginal, year, month, day, strategy) for file, (datetimeoriginal, year, month, day, strategy) in
                      _get_metadata(*paths)]
        inserted = _insert_records(conn, *collection) - deleted
    return deleted, inserted


def select(database: Union[str, PurePath], year: Optional[int] = None) -> Iterable[Tuple[str, str, int, int, int, int, int]]:
    with DatabaseConnection(str(database)) as conn:
        for item in _select_records(conn, year=year):
            yield item


# ===================
# Private interfaces.
# ===================
def _get_metadata(*paths: Union[str, PurePath]):
    strategies = {}
    with open(that_file.parent / "Resources" / "strategies.yml") as stream:
        strategies = yaml.load(stream)
    collection = OrderedDict()  # type: Dict[str, Tuple[int, int, int, int, int]]
    args = [str(PurePath(expandvars("%_RESOURCES%")) / "exiftool.exe"),
            "-r",
            "-d",
            "%Y%m%d",
            "-j",
            "-charset",
            "Latin1",
            "-DateTimeOriginal",
            "-fileOrder",
            "DateTimeOriginal",
            "-ext",
            "jpg"]
    for path in paths:
        with TemporaryFile(mode="r+", encoding="UTF_8") as stream:
            _args = list(args)
            _args.append(str(path))
            _year = int(PurePath(path).parts[1][:4])  # type: int
            process = run(_args, stdout=stream, stderr=PIPE, universal_newlines=True)
            if not process.returncode:
                stream.seek(0)
                try:
                    mapping = json.load(stream)
                except json.decoder.JSONDecodeError:
                    pass
                else:
                    for item in mapping:
                        with suppress(KeyError):
                            key = item["SourceFile"]  # type: str
                            value = item["DateTimeOriginal"]  # type: int
                            collection[key] = (value, int(str(value)[:4]), int(str(value)[4:6]), int(str(value)[6:8]), strategies.get(_year, 0))
    for item in collection.items():
        yield item


def _delete_records(db_connector, *args: Union[str, PurePath]) -> int:
    with db_connector:
        db_connector.executemany("DELETE FROM images WHERE parent=?", [("/".join(path.parts[1:]),) for path in map(PurePath, args)])
    return db_connector.total_changes


def _insert_records(db_connector, *args: Tuple[str, str, int, int, int, int, int]) -> int:
    with db_connector:
        db_connector.executemany("INSERT INTO images (parent, name, datetimeoriginal, year, month, day, strategy) VALUES(?, ?, ?, ?, ?, ?, ?)", args)
    return db_connector.total_changes


def _select_records(db_connector, year=None):
    statement = "SELECT parent, name, datetimeoriginal, year, month, day, strategy FROM images"
    args = ()
    if year:
        statement = f"{statement} WHERE year=?"
        args = (year,)
    statement = f"{statement} ORDER BY year, month, name"
    for row in db_connector.execute(statement, args):
        yield (row["parent"], row["name"], row["datetimeoriginal"], row["year"], row["month"], row["day"], row["strategy"])


# =============================
# Script if module run as main.
# =============================
if __name__ == "__main__":
    import argparse
    import operator
    import re
    from Applications.parsers import database_parser


    class SetPurePath(argparse.Action):
        """

        """

        def __init__(self, option_strings, dest, **kwargs):
            super().__init__(option_strings, dest, **kwargs)

        def __call__(self, parsobj, namespace, values, option_string=None):
            setattr(namespace, self.dest, list(map(PurePath, values)))


    regex = re.compile(r"^\d{4,6}$")

    parser = argparse.ArgumentParser(parents=[database_parser])
    parser.add_argument("paths", nargs="+", action=SetPurePath)
    parser.add_argument("--dont_delete", action="store_true")
    arguments = parser.parse_args()
    for path in arguments.paths:
        for root, dirs, files in os.walk(path):
            if files:
                match = regex.match(PurePath(root).parts[1])
                if match:
                    deleted, inserted = main(arguments.db, PurePath(root), delete=operator.not_(arguments.dont_delete))
                    print("# ----- #")
                    print(root)
                    print(deleted)
                    print(inserted)
