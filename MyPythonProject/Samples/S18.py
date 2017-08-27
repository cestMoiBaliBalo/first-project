# -*- coding: utf-8 -*-
import sqlite3


__author__ = 'Xavier ROSSET'


# read = sqlite3.connect(r"G:\Computing\database_sav (103 - 104).db", detect_types=sqlite3.PARSE_DECLTYPES)
write = sqlite3.connect(r"G:\Computing\database.db", detect_types=sqlite3.PARSE_DECLTYPES)
# status = 0
#
# for row in read.execute("SELECT albumid, discid, trackid, title, created FROM tracks WHERE rowid BETWEEN ? and ? ORDER BY rowid", (103, 104)):
#     with write:
#         write.execute("INSERT INTO tracks (albumid, discid, trackid, title, created) VALUES(?, ?, ?, ?, ?)", row)
#         status = write.total_changes
# print(status)
#
# for row in write.execute("SELECT rowid, a.* FROM tracks a ORDER BY rowid"):
#     print(row)

write.executemany("UPDATE albums SET albumid=? WHERE rowid between ? and ?", [("C.Cradle of Filth.1.20040000.1", 127, 127)])
write.commit()
