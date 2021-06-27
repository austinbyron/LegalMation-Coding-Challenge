import sqlite3

"""
**********  Run this program before the first time you run App.py   ***********

You only need to run this program once to create the database

"""

conn = sqlite3.connect('database.db')
print('Connected to database')

conn.execute('CREATE TABLE extractions (docid TEXT, plaintiff TEXT, defendant TEXT, date TEXT)')
print('Created table')

conn.close()