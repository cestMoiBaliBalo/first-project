# -*- coding: utf-8 -*-
from Applications.shared import DATABASE
import sqlite3

__author__ = 'Xavier ROSSET'


if __name__ == "__main__":

    c = sqlite3.connect(DATABASE)
    c.execute("DROP TABLE IF EXISTS lastrundates")
    # c.execute("CREATE TABLE IF NOT EXISTS encoders (encoder TOTO NOT NULL)")
    # c.execute("INSERT INTO encoders (encoder) VALUES (?)", (Encoder("FLAC", "13", "1.Lossless Audio Codec", "some informations"),))
    # for row in c.execute("SELECT encoder FROM encoders ORDER BY encoder"):
    #     print(row["encoder"].name)
    #     print(row["encoder"].code)
    #     print(row["encoder"].folder)
    #     print(row["encoder"].information)
    c.close()
