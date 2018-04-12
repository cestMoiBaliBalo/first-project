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
        _unixepochtime = shared.validdatetime(time)
    except ValueError as err:
        raise argparse.ArgumentTypeError(err)
    else:
        _unixepochtime = _unixepochtime[0]
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
#  3. PARSER 3.
#     =========
database_parser = argparse.ArgumentParser(description="Shared parser for database arguments.", add_help=False)
group = database_parser.add_mutually_exclusive_group()
group.add_argument("--database", nargs="?", default=shared.DATABASE, help="Path to database storing digital albums.", type=database, dest="db")
group.add_argument("-t", "--test", nargs="?", default=False, const=True, action=shared.SetDatabase, help="Use test database.")

#     =========
#  4. PARSER 4.
#     =========
readtable = argparse.ArgumentParser(parents=[database_parser])
readtable.add_argument("table", choices=["tasks"], help="Read table")

#     =========
#  5. PARSER 5.
#     =========
loglevel_parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS, add_help=False)
loglevel_parser.add_argument("--loglevel", help="Log level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

#     =========
#  6. PARSER 6.
#     =========
subset_parser = argparse.ArgumentParser(parents=[database_parser], argument_default=argparse.SUPPRESS)
subset_parser.add_argument("--artistsort", nargs="*", help="Subset digital albums by artistsort.")
subset_parser.add_argument("--albumsort", nargs="*", help="Subset digital albums by albumsort.")
subset_parser.add_argument("--artist", nargs="*", help="Subset digital albums by artist.")

#     =========
#  7. PARSER 7.
#     =========
tasks_parser = argparse.ArgumentParser()
tasks_parser.add_argument("-t", "--table", default="tasks", choices=["tasks"])
subparser = tasks_parser.add_subparsers(dest="action")
parser_select = subparser.add_parser("select", argument_default=argparse.SUPPRESS, parents=[loglevel_parser, database_parser])
parser_select.add_argument("taskid", type=int)
parser_select.add_argument("--days", default=10, type=int)
parser_select.add_argument("--dontcreate", action="store_true")
parser_select.add_argument("--forced", action="store_true")
parser_update = subparser.add_parser("update", argument_default=argparse.SUPPRESS, parents=[loglevel_parser, database_parser])
parser_update.add_argument("taskid", type=int)

#     =========
#  8. PARSER 8.
#     =========

# --------------
# Parent parser.
# --------------
images_pparser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS, add_help=False)
images_pparser.add_argument("files", nargs="+", help="Source directories or images")
images_pparser.add_argument("--ext", nargs="*", dest="extensions", default=["jpg"])
images_pparser.add_argument("--test", action="store_true")

# -------------
# Child parser.
# -------------
images_cparser = argparse.ArgumentParser()
subparser = images_cparser.add_subparsers(dest="script")

# --> Rename images.
images_rename = subparser.add_parser("rename", argument_default=argparse.SUPPRESS, parents=[images_pparser, loglevel_parser])
images_rename.add_argument("--index", default="1", type=int, help="Starting index")

# --> Write tags.
images_write = subparser.add_parser("write", argument_default=argparse.SUPPRESS, parents=[images_pparser, loglevel_parser])
images_write.add_argument("--city")
images_write.add_argument("--location")
images_write.add_argument("--keywords", nargs="*")
images_write.add_argument("--copyright", action="store_true")

# --> Read tags.
images_read = subparser.add_parser("read", argument_default=argparse.SUPPRESS, parents=[images_pparser, loglevel_parser])

#     =========
#  9. PARSER 9.
#     =========
foldercontent = argparse.ArgumentParser()
subparser = foldercontent.add_subparsers(dest="command")

# -----
parser1 = subparser.add_parser("1")
parser1.add_argument("extensions", nargs="*", help="only given extensions. Facultative", default=[])

# -----
parser2 = subparser.add_parser("2")
parser2.add_argument("group", nargs="+", choices=["computing", "documents", "lossless", "lossy", "music"], action=shared.GetExtensions)
group = parser2.add_mutually_exclusive_group()
group.add_argument("-e", "--excl", dest="exclude", nargs="*", action=shared.ExcludeExtensions, help="exclude enumerated extension(s)")
group.add_argument("-k", "--keep", nargs="*", action=shared.KeepExtensions, help="exclude all extensions but enumerated extension(s)")
parser2.add_argument("-i", "--incl", dest="include", nargs="*", action=shared.IncludeExtensions, help="include enumerated extension(s)")

# -----
parser3 = subparser.add_parser("3")
parser3.add_argument("extensions", nargs="+", help="excluded extensions. Mandatory.")
