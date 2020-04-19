'''anime app database api'''

import sqlite3
import os

DB_FILENAME = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'var', 'anime.sqlite3')

def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def getDB():
    '''use this function to get the connection to db
    Remember to use commit and close function!!
    Returns
    -------
    database connection object
    '''
    conn = sqlite3.connect(DB_FILENAME)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON")
    return conn