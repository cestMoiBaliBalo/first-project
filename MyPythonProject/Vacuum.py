# -*- coding: utf-8 -*-
from Applications.shared import DATABASE
import sqlite3

__author__ = 'Xavier ROSSET'


conn = sqlite3.connect(DATABASE)
conn.execute("VACUUM")
conn.close()
