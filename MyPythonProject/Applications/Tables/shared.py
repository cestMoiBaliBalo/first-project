# -*- coding: utf-8 -*-
# pylint: disable=empty-docstring, invalid-name, line-too-long
__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__status__ = "Production"

import logging
import operator
import re
import sqlite3
from contextlib import ContextDecorator, ExitStack
from functools import partial
from itertools import compress
from typing import Any, Optional, Tuple

from ..shared import DATABASE, DFTDAYREGEX, DFTMONTHREGEX, DFTYEARREGEX


# ========
# Classes.
# ========
class DatabaseConnection(ContextDecorator):
    def __init__(self, db: str = DATABASE) -> None:
        self.database = db

    def __enter__(self):
        self.conn = sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


# ==================
# Private functions.
# ==================
def _contains(a, b):
    return operator.contains(b, a)


# ==========
# Functions.
# ==========
def adapt_booleanvalue(boolobj):
    """
    Adapt a python boolean value to an integer value accepted by sqlite3 module.
    :param boolobj: object created from `ToBoolean` class.
    """
    d = {False: 0, True: 1}
    return d[boolobj.boolean_value]


def convert_tobooleanvalue(i: bytes) -> bool:
    """
    Convert an integer value to a python boolean value.
    :param i: integer value.
    """
    return bool(int(i))


def close_database(conn):
    """

    :param conn:
    :return:
    """
    conn.close()


def get_rawdata(table, db=DATABASE):
    """

    :param table:
    :param db:
    :return:
    """
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    curs = conn.cursor()
    curs.execute("SELECT * FROM {0} ORDER BY rowid".format(table))
    for record in curs.fetchall():
        yield record


# ===============================
# Protected functions interfaces.
# ===============================
def set_setclause(**kwargs: Any) -> Tuple[str, Tuple[str, ...]]:
    return _set_setclause(**kwargs)


def set_whereclause_album(*keys: str) -> Tuple[str, Tuple[str, ...]]:
    return _set_whereclause_album(*keys)


def set_whereclause_disc(*keys: str) -> Tuple[Optional[str], Any]:
    return _set_whereclause_disc(*keys)


def set_whereclause_track(*keys: str) -> Tuple[Optional[str], Any]:
    return _set_whereclause_track(*keys)


def run_statement(statement: str, *args: Any, db: str = DATABASE) -> int:
    return _run_statement(statement, *args, db=db)


# =======================================================
# These interfaces mustn't be used from external scripts.
# =======================================================
def _split_discid(discid: str) -> Tuple[Optional[str], Optional[int]]:
    """
    :param discid:
    :return:
    """
    _albumid, _discid = None, None  # type: Optional[str], Optional[int]
    rex1 = re.compile(r"^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{{8}}\.\d\.D\d$)(.\.(?:{0})(?:{1})(?:{2})\.\d)\.D(\d)$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX))
    rex2 = re.compile(r"^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{{8}}\.\d\.D\d$)(.\.(?:{0})0000\.\d)\.D(\d)$".format(DFTYEARREGEX))
    match = rex1.match(discid)
    if not match:
        match = rex2.match(discid)
    if match:
        _albumid = match.group(1)
        _discid = int(match.group(2))
    return _albumid, _discid


def _split_trackid(trackid: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """
    :param trackid:
    :return:
    """
    _albumid, _discid, _trackid = None, None, None  # type: Optional[str], Optional[int], Optional[int]
    rex1 = re.compile(r"^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{{8}}\.\d\.D\d\.T\d{{2}}$)(.\.(?:{0})(?:{1})(?:{2})\.\d)\.D(\d)\.T(\d{{2}})$".format(DFTYEARREGEX, DFTMONTHREGEX, DFTDAYREGEX))
    rex2 = re.compile(r"^(?=[\d.]+$)(?=.\.[^.]+\..$)(?=\d\.\d{{8}}\.\d\.D\d\.T\d{{2}}$)(.\.(?:{0})0000\.\d)\.D(\d)\.T(\d{{2}})$".format(DFTYEARREGEX))
    match = rex1.match(trackid)
    if not match:
        match = rex2.match(trackid)
    if match:
        _albumid = match.group(1)
        _discid = int(match.group(2))
        _trackid = int(match.group(3))
    return _albumid, _discid, _trackid


def _set_setclause(**kwargs: Any) -> Tuple[str, Tuple[Any, ...]]:
    """
    :param kwargs:
    :return:
    """
    args, clause = (), ""  # type: Tuple[Any, ...], str
    for key, value in kwargs.items():
        clause = f"{clause}{key}=?, "
        args += (value,)
    return clause[:-2], args


def _set_whereclause_album(*keys: str) -> Tuple[str, Tuple[str, ...]]:
    """
    :param keys:
    :return:
    """
    clause = " OR ".join(["albumid=?"] * len(keys))  # type: str
    argw = ()  # type: Tuple[str, ...]
    for key in keys:
        argw += (key,)
    return clause, argw


def _set_whereclause_disc(*keys: str) -> Tuple[Optional[str], Any]:
    """
    :param keys:
    :return:
    """
    clause, argw = None, None  # type: Optional[str], Any
    _keys = list(compress(map(_split_discid, keys), map(operator.not_, map(partial(_contains, None), map(_split_discid, keys)))))  # [("1.20180000.1", 1), ("1.20180000.1", 2)]  type: List[Tuple[str, int]]
    if _keys:
        argw = ()
        clause = " OR ".join(["(albumid=? AND discid=?)"] * len(_keys))
        for key in _keys:
            argw += key
    return clause, argw


def _set_whereclause_track(*keys: str) -> Tuple[Optional[str], Any]:
    """
    :param keys:
    :return:
    """
    clause, argw = None, None  # type: Optional[str], Any
    _keys = list(
            compress(map(_split_trackid, keys),
                     map(operator.not_, map(partial(_contains, None), map(_split_trackid, keys)))))  # [("1.20180000.1", 1, 1), ("1.20180000.1", 1, 2)]  type: List[Tuple[str, int, int]]
    if _keys:
        argw = ()
        clause = " OR ".join(["(albumid=? AND discid=? AND trackid=?)"] * len(_keys))
        for key in _keys:
            argw += key
    return clause, argw


def _run_statement(statement: str, *args: Any, db: str = DATABASE) -> int:
    """

    :param statement:
    :param args:
    :param db:
    :return:
    """
    in_logger = logging.getLogger("{0}._run_statement".format(__name__))
    changes: int = 0
    in_logger.debug(statement)
    in_logger.debug(args)
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        try:
            conn.execute(statement, args)
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as err:
            in_logger.exception(err)
            stack.pop_all()
            stack.callback(close_database, conn)
        finally:
            changes = conn.total_changes
    return changes
