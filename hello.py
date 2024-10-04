#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3 as lite
import csv
import pandas

con = lite.connect("test.db")  # change to 'sqlite:///your_filename.db'
cur = con.cursor()
# use your column names here
with con:
    con.execute("drop table players")
    con.execute(
        "CREATE TABLE players (name, cost INTEGER, position, points INTEGER, dollarcost, roi DECIMAL);")

# df = pandas.read_csv("players.csv")
# print(df)
# df.to_sql("players", con, if_exists='append', index=False)

with open('players.csv', 'r') as fin:  # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin)  # comma is default delimiter
#     print(dr)
    to_db = [(i['name'], i['cost'], i['position'],
              i['points'], i['ppd'], i['roi']) for i in dr]
#     print(to_db)

cur.execute('delete from players')
cur.executemany(
    "INSERT INTO players (name, cost, position, points, dollarcost, roi) VALUES (?, ?, ?, ?, ?, ?);", to_db)
con.commit()
con.close()


# def writeData(data):

#     f = open('cars.sql', 'w')

#     with f:
#         f.write(data)


# con = lite.connect('test.db')

# with con:

#     con.row_factory = lite.Row

#     cur = con.cursor()
#     cur.execute("SELECT * FROM cars")

#     rows = cur.fetchall()

#     for row in rows:
#         print(f'{row["id"]} {row["name"]} ${row["price"]}')

#     data = '\n'.join(con.iterdump())

#     writeData(data)
