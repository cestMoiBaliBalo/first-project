# -*- coding: utf-8 -*-
import sqlite3
import logging
from itertools import repeat
from datetime import datetime,timedelta
from Applications.shared import DATABASE

__author__ = 'Xavier ROSSET'


# =========
# Mappings.
# =========
MAPPING = {"rundates": "rundate", "backups": "backup"}


# ===================================
# Main functions to work with tables.
# ===================================
def select(table, db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for row in conn.execute("SELECT * FROM {0} ORDER BY id".format(table)):
        logger = logging.getLogger("{0}.select".format(__name__))
        logger.debug("Table          : {0}".format(table))
        logger.debug("Selected record:")
        for item in tuple(row):
            logger.debug("\t{0}".format(item).expandtabs(3))
        yield tuple(row)


def selectfromuid(uid, table, db=DATABASE):

    # Log arguments.
    logger = logging.getLogger("{0}.selectfromuid".format(__name__))
    logger.debug("Database: {0}.".format(db))
    logger.debug("Table   : {0}.".format(table))
    logger.debug("ID      : {0:>3d}.".format(uid))

    # Get data relative to record unique ID.
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    curs = conn.cursor()
    curs.execute("SELECT * FROM {0} WHERE rowid=?".format(table), (uid,))
    record = curs.fetchone()
    conn.close()

    # Return found data.
    return record


def insert(*uid, db=DATABASE, table=None, date=None):
    if table is None:
        return 0
    if table not in MAPPING:
        return 0
    if date is None:
        date = datetime.utcnow()
    conn = sqlite3.connect(db)
    with conn:
        conn.executemany("INSERT INTO {0} (id, {1}) VALUES(?, ?)".format(table, MAPPING[table]), zip(uid, repeat(date)))
        status = conn.total_changes
        logger = logging.getLogger("{0}.insert".format(__name__))
        logger.debug("Database: {0}.".format(db))
        logger.debug("Table   : {0}.".format(table))
        logger.debug("{0:>3d} records inserted.".format(status))
        if status:
            for item in uid:
                logger.debug("ID      : {0:>3d}.".format(item))
    return status


def update(uid, table, db=DATABASE, date=None):

    if table not in MAPPING:
        return 0
    if date is None:
        date = datetime.utcnow()
    recordid = selectfromuid(uid, table, db)

    # Record exists: it is updated.
    if recordid:
        status, conn = 0, sqlite3.connect(db)
        with conn:
            conn.execute("UPDATE {0} SET {1}=? WHERE id=?".format(table, MAPPING[table]), (date, uid))
            status = conn.total_changes
        return status

    # Record doesn't exist: it is inserted.
    return insert(uid, db=db, table=table, date=date)


def deletefromuid(*uid, table, db=DATABASE):
    if table not in MAPPING:
        return 0
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.executemany("DELETE FROM {0} WHERE id=?".format(table), [(i,) for i in uid])
        status = conn.total_changes
        logger = logging.getLogger("{0}.deletefromuid".format(__name__))
        logger.debug("Database: {0}.".format(db))
        logger.debug("Table   : {0}.".format(table))
        logger.debug("{0:>3d} records removed.".format(status))
        if status:
            for item in uid:
                logger.debug("ID      : {0:>3d}.".format(item))
    return status


def delete(table, db=DATABASE):
    if table not in MAPPING:
        return 0
    status, conn = 0, sqlite3.connect(db)
    with conn:
        conn.execute("DELETE FROM {0}".format(table))
        status = conn.total_changes
        logger = logging.getLogger("{0}.delete".format(__name__))
        logger.debug("Database: {0}.".format(db))
        logger.debug("Table   : {0}.".format(table))
        logger.debug("{0:>3d} records removed.".format(status))
    return status


def isdeltareached(uid, table, db=DATABASE, days=10):
    logger = logging.getLogger("{0}.isdeltareached".format(__name__))
    deltareached = True
    record = selectfromuid(uid, table, db)
    if record:
        if datetime.utcnow() - record[1] < timedelta(days=days):
            deltareached = False
    logger.debug(deltareached)
    return deltareached
