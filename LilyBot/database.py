# database.py  –  Thin SQLite wrapper

import sqlite3
import threading
from config import DATABASE

_local = threading.local()


def get_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(DATABASE, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _init_tables(_local.conn)
    return _local.conn


def _init_tables(conn: sqlite3.Connection):
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS warnings (
            chat_id   INTEGER,
            user_id   INTEGER,
            count     INTEGER DEFAULT 0,
            reasons   TEXT    DEFAULT '',
            PRIMARY KEY (chat_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS warn_settings (
            chat_id   INTEGER PRIMARY KEY,
            limit_    INTEGER DEFAULT 3,
            action    TEXT    DEFAULT 'ban'
        );

        CREATE TABLE IF NOT EXISTS welcome_settings (
            chat_id         INTEGER PRIMARY KEY,
            welcome_enabled INTEGER DEFAULT 1,
            goodbye_enabled INTEGER DEFAULT 1,
            welcome_text    TEXT    DEFAULT '',
            goodbye_text    TEXT    DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS filters (
            chat_id  INTEGER,
            keyword  TEXT,
            response TEXT,
            PRIMARY KEY (chat_id, keyword)
        );

        CREATE TABLE IF NOT EXISTS flood_settings (
            chat_id INTEGER PRIMARY KEY,
            limit_  INTEGER DEFAULT 0
        );
    """)
    conn.commit()


# ── Convenience helpers ──────────────────────────────────────────────────────

def fetchone(sql, params=()):
    return get_conn().execute(sql, params).fetchone()

def fetchall(sql, params=()):
    return get_conn().execute(sql, params).fetchall()

def execute(sql, params=()):
    conn = get_conn()
    conn.execute(sql, params)
    conn.commit()
