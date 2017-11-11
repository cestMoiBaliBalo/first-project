# -*- coding: utf-8 -*-
import argparse

from . import shared

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"


#  ==========
#  Functions.
#  ==========
def unixepochtime(time):
    """

    :param time:
    :return:
    """
    try:
        _unixepochtime = shared.validtimestamp(time)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _unixepochtime


def database(db):
    """

    :param db:
    :return:
    """
    try:
        _database = shared.validdb(db)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    return _database


#     =========
#  1. PARSER 1.
#     =========
zipfile = argparse.ArgumentParser()
zipfile.add_argument("source", type=shared.validpath)
zipfile.add_argument("destination", choices=["documents", "backup", "temp", "onedrive"], action=shared.GetPath)
subparsers = zipfile.add_subparsers()

# Singled extensions.
parser1_s = subparsers.add_parser("singled")
parser1_s.add_argument("extensions", nargs="+")

# Grouped extensions.
parser1_g = subparsers.add_parser("grouped")
parser1_g.add_argument("group", nargs="+", choices=["documents", "computing"], action=shared.GetExtensions)
group = parser1_g.add_mutually_exclusive_group()
group.add_argument("-e", "--excl", dest="exclude", nargs="*", action=shared.ExcludeExtensions, help="exclude enumerated extension(s)")
group.add_argument("-k", "--keep", nargs="*", action=shared.KeepExtensions, help="exclude all extensions but enumerated extension(s)")
parser1_g.add_argument("-i", "--incl", dest="include", nargs="*", action=shared.IncludeExtensions, help="include enumerated extension(s)")

#     =========
#  2. PARSER 2.
#     =========
epochconverter = argparse.ArgumentParser()
epochconverter.add_argument("beg", help="Beginning epoch", type=unixepochtime)
epochconverter.add_argument("end", help="End epoch", type=unixepochtime, nargs="?", action=shared.SetEndSeconds)
epochconverter.add_argument("-z", "--zone", help="Time zone", default=shared.DFTTIMEZONE)

#     =========
#  4. PARSER 4.
#     =========
foldercontent = argparse.ArgumentParser()
foldercontent.add_argument("folder", type=shared.validpath)
foldercontent.add_argument("extensions", nargs="*")

#     =========
#  5. PARSER 5.
#     =========
improvedfoldercontent = argparse.ArgumentParser()
improvedfoldercontent.add_argument("folder", type=shared.validpath)
improvedfoldercontent.add_argument("excluded", nargs="*")
improvedfoldercontent.add_argument("-e", "--ext", dest="extensions", nargs="*")

#     =========
#  6. PARSER 6.
#     =========
readtable = argparse.ArgumentParser()
readtable.add_argument("table", choices=["rundates", "backups"], help="Read table")
readtable.add_argument("database", nargs="?", default=shared.DATABASE, type=database, help="Read database")

#     =========
#  7. PARSER 7.
#     =========
database_parser = argparse.ArgumentParser(description="Shared parser for database arguments.", add_help=False)
group = database_parser.add_mutually_exclusive_group()
group.add_argument("--database", dest="db", default=shared.DATABASE, help="Path to database storing digital albums.", type=database)
group.add_argument("--test", nargs="?", const=True, default=False, action=shared.SetDatabase, help="Use test database.")
