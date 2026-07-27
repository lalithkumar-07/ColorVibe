"""
database/db.py
---------------
Small helper layer around mysql-connector-python.

All queries elsewhere in the app go through get_connection()/get_cursor()
so there is exactly one place that owns connection settings, and every
query is executed with parameter placeholders (%s) rather than string
formatting, which is what actually prevents SQL injection.
"""

import mysql.connector
from mysql.connector import Error as MySQLError
from flask import current_app, g


def get_connection():
    """
    Return a MySQL connection for the current request, creating one and
    stashing it on Flask's `g` object if it doesn't exist yet. This means
    a single request reuses one connection instead of opening several.
    """
    if "db_conn" not in g:
        cfg = current_app.config
        g.db_conn = mysql.connector.connect(
            host=cfg["MYSQL_HOST"],
            port=cfg["MYSQL_PORT"],
            user=cfg["MYSQL_USER"],
            password=cfg["MYSQL_PASSWORD"],
            database=cfg["MYSQL_DATABASE"],
            autocommit=False,
        )
    return g.db_conn


def close_connection(exception=None):
    """Close the request-scoped connection, if one was opened."""
    conn = g.pop("db_conn", None)
    if conn is not None and conn.is_connected():
        conn.close()


def get_cursor(dictionary=True):
    """Return a cursor for the shared connection. dictionary=True gives dict rows."""
    return get_connection().cursor(dictionary=dictionary)


def init_app(app):
    """Register the connection teardown with the Flask app."""
    app.teardown_appcontext(close_connection)


def execute(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Convenience wrapper for the common query patterns used throughout the app.

    - Always uses parameterized queries (params is a tuple/list of values).
    - commit=True is used for INSERT/UPDATE/DELETE.
    - fetchone/fetchall are used for SELECTs.
    Returns the cursor's lastrowid for inserts, the fetched row(s), or None.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        if commit:
            conn.commit()
            result = cursor.lastrowid
        return result
    except MySQLError:
        conn.rollback()
        raise
    finally:
        cursor.close()
