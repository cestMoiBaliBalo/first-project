# -*- coding: utf-8 -*-
import sqlite3
from Applications.shared import DATABASE

__author__ = 'Xavier ROSSET'


conn = sqlite3.connect(DATABASE)
conn.execute("ALTER TABLE albums ADD COLUMN count NOT NULL DEFAULT 0")
conn.commit()
conn.close()
