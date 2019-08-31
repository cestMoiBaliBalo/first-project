# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import logging.config
import sqlite3
from contextlib import ExitStack, suppress
from datetime import datetime, timedelta
from functools import partial
from operator import add, eq
from typing import Iterable, Optional, Tuple

import iso8601
import yaml

from ..shared import DatabaseConnection, close_database
from ...parsers import tasks_parser
from ...shared import DATABASE, LOCAL, UTC, UTF8, get_dirname, itemgetter_

__author__ = 'Xavier ROSSET'
__maintainer__ = 'Xavier ROSSET'
__email__ = 'xavier.python.computing@protonmail.com'
__changes__ = "Production"


# ===================================
# Main interfaces to work with tasks.
# ===================================
def exist_task(taskid: int, *, db: str = DATABASE) -> bool:
    with DatabaseConnection(db) as conn:
        tasks = set(row["taskid"] for row in conn.execute("SELECT taskid FROM tasks"))
    return taskid in tasks


def get_tasks(db: str = DATABASE) -> Iterable[Tuple[int, datetime]]:
    for taskid, utc_run in _get_tasks(db):
        yield taskid, utc_run


def get_task(taskid: int, *, db: str = DATABASE) -> Tuple[int, Optional[datetime]]:
    return _get_task(taskid, db=db)


def insert_task(taskid: int, *, db: str = DATABASE, dtobj: datetime = datetime.utcnow()) -> int:
    return _insert_task(taskid, db=db, dtobj=dtobj)


def update_task(taskid: int, *, db: str = DATABASE, dtobj: datetime = datetime.utcnow()) -> int:
    """

    :param taskid:
    :param db:
    :param dtobj:
    :return:
    """

    # Record exists: it is updated.
    if exist_task(taskid, db=db):
        return _update_task(taskid, db=db, dtobj=dtobj)

    # Record doesn't exist: it is inserted.
    return _insert_task(taskid, db=db, dtobj=dtobj)


def delete_task(taskid: int, *, db: str = DATABASE) -> int:
    """

    :param taskid:
    :param db:
    :return:
    """
    return _delete_task(taskid, db=db)


def run_task(taskid: int, *, db: str = DATABASE, delta: int = 10) -> bool:
    """

    :param taskid:
    :param db:
    :param delta:
    :return:
    """
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared.run_task")
    in_logger.debug("Database: %s", db)
    if exist_task(taskid, db=db):
        _, utc_run = _get_task(taskid, db=db)
        return UTC.localize(datetime.utcnow()) - UTC.localize(utc_run) >= timedelta(days=delta)
    in_logger.debug("%s task(s) inserted.", _insert_task(taskid, db=db))
    return True


# =======================================================
# These interfaces mustn't be used from external scripts.
# =======================================================
def _get_tasks(db: str = DATABASE) -> Iterable[Tuple[int, datetime]]:
    with DatabaseConnection(db) as conn:
        for taskid, utc_run in ((row["taskid"], row["utc_run"]) for row in conn.execute("SELECT taskid, utc_run FROM tasks")):
            yield taskid, utc_run


def _get_task(taskid: int, *, db: str = DATABASE) -> Tuple[int, Optional[datetime]]:
    uid, utc_run = 0, None  # type: int, Optional[datetime]
    it = filter(itemgetter_()(partial(eq, taskid)), _get_tasks(db))
    with suppress(StopIteration):
        uid, utc_run = next(it)
    return uid, utc_run


def _insert_task(taskid: int, *, db: str = DATABASE, dtobj: datetime = datetime.utcnow()) -> int:
    """

    :param taskid:
    :param db:
    :param dtobj:
    :return:
    """
    changes: int = 0

    # Log arguments.
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared._insert_task")
    in_logger.debug("Database: %s", db)

    # Insert record.
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        try:
            conn.execute("INSERT INTO tasks (taskid, utc_run) VALUES(?, ?)", (taskid, dtobj))
        except sqlite3.IntegrityError as err:
            in_logger.exception(err)
            stack.pop_all()
            stack.callback(close_database, conn)
        finally:
            changes = conn.total_changes
    in_logger.debug("%s records inserted.", changes)
    return changes


def _update_task(taskid: int, *, db: str = DATABASE, dtobj: datetime = datetime.utcnow()) -> int:
    """

    :param taskid:
    :param db:
    :param dtobj:
    :return:
    """

    # Log arguments.
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared._update_task")
    in_logger.debug("Database: %s", db)
    in_logger.debug("Row ID  : %s", taskid)

    # Update record.
    changes: int = 0
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        try:
            conn.execute("UPDATE tasks SET utc_run=? WHERE rowid=?", (dtobj, taskid))
        except sqlite3.OperationalError as err:
            in_logger.exception(err)
            stack.pop_all()
            stack.callback(close_database, conn)
        finally:
            changes = conn.total_changes
    in_logger.debug("%s record(s) updated.", changes)
    return changes


def _delete_task(taskid: int, *, db: str = DATABASE) -> int:
    """

    :param taskid:
    :param db:
    :return:
    """
    in_logger = logging.getLogger("Applications.Tables.Tasks.shared._delete_task")
    in_logger.debug("Database: %s", db)
    in_logger.debug("Row ID  : %s", taskid)
    changes: int = 0
    with ExitStack() as stack:
        conn = stack.enter_context(DatabaseConnection(db))
        stack.enter_context(conn)
        try:
            conn.execute("DELETE FROM tasks WHERE rowid=?", (taskid,))
        except sqlite3.OperationalError:
            stack.pop_all()
            stack.callback(close_database, conn)
        finally:
            changes = conn.total_changes
    in_logger.debug("%s record(s) deleted.", changes)
    return changes


# ===============================================
# Main algorithm if module is run as main script.
# ===============================================
if __name__ == "__main__":

    import locale
    import os
    import sys

    # Set French environment.
    locale.setlocale(locale.LC_ALL, ("french", "fr_FR.ISO8859-1"))

    # Local constants.
    LOG_LEVELS = {False: "info", True: "debug"}
    EXIT = {False: 0, True: 1}

    # Get arguments.
    arguments = vars(tasks_parser.parse_args())

    # Configure logging.
    with open(os.path.join(get_dirname(os.path.abspath(__file__), level=4), "Resources", "logging.yml"), encoding=UTF8) as fp:
        config = yaml.load(fp)
    for logger in ["Applications.Tables.Tasks"]:
        with suppress(KeyError):
            config["loggers"][logger]["level"] = LOG_LEVELS[arguments.get("debug", False)].upper()
    logging.config.dictConfig(config)

    # Check task: can it be run?
    if arguments.get("action") == "check":
        sys.exit(EXIT[run_task(arguments["taskid"],
                               db=arguments.get("db", DATABASE),
                               delta=arguments.get("delta", 10))])

    # Update task.
    if arguments.get("action") == "update":
        datobj = datetime.utcnow()
        timestamp = arguments.get("timestamp", 0)
        datstring = arguments.get("datstring", "")
        if timestamp:
            datobj = LOCAL.localize(datetime.fromtimestamp(timestamp)).astimezone(UTC).replace(tzinfo=None)
        elif datstring:
            datobj = LOCAL.localize(iso8601.parse_date(datstring).replace(tzinfo=None)).astimezone(UTC).replace(tzinfo=None)
        sys.exit(update_task(arguments["taskid"],
                             db=arguments.get("db", DATABASE),
                             dtobj=arguments.get("func", add)(datobj, timedelta(days=arguments.get("days", 0)))))
