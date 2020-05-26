# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
import argparse
import locale
import os
from pathlib import Path
from typing import Any

from Applications.Tables.shared import DatabaseConnection
from Applications.shared import pprint_sequence

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Development"

_ME = Path(os.path.abspath(__file__))
_MYNAME = Path(os.path.abspath(__file__)).stem
_MYPARENT = Path(os.path.abspath(__file__)).parent

# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


class GetStatement(argparse.Action):
    """

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(GetStatement, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parsobj, namespace, values, option_string=None):
        mapping = {"applications": "SELECT applicationid, application FROM applications ORDER BY application",
                   "countries": "SELECT countryid, country FROM countries ORDER BY country",
                   "genres": "SELECT genreid, genre FROM genres ORDER BY genre",
                   "languages": "SELECT languageid, language FROM languages ORDER BY language",
                   "providers": "SELECT providerid, provider FROM providers ORDER BY provider",
                   "supports": "SELECT supportid, support FROM supports ORDER BY support"}
        setattr(namespace, self.dest, values)
        setattr(namespace, "statement", mapping.get(values))


parser = argparse.ArgumentParser()
parser.add_argument("table", choices=["applications", "countries", "genres", "languages", "providers", "supports"], action=GetStatement)
arguments = parser.parse_args()

collection = []  # type: Any
if arguments.statement:
    with DatabaseConnection() as conn:
        collection = enumerate([row[1] for row in conn.execute(arguments.statement)], start=1)
if collection:
    indexes, values = zip(*collection)
    for index, genre in zip(pprint_sequence(*indexes, align=">"), values):
        print(f"{index}. {genre}")
# with DatabaseConnection() as conn:
#     conn.execute("INSERT INTO countries (country) VALUES ('Norway')")
#     conn.commit()

