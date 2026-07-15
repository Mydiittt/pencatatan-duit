"""
database/db.py
Mengelola koneksi SQLite dan pembuatan skema tabel.
Ini adalah lapisan paling bawah yang digunakan oleh semua Model.
"""

import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, DEFAULT_INCOME_CATEGORIES, DEFAULT_EXPENSE_CATEGORIES


class Database:
    """Singleton sederhana untuk koneksi database SQLite."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path=DB_PATH):
        if self._initialized:
            return
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._seed_categories()
        self._initialized = True

    def _create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                icon TEXT DEFAULT '💰',
                UNIQUE(name, type)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                amount REAL NOT NULL,
                category_id INTEGER,
                note TEXT,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE,
                UNIQUE(category_id, month, year)
            )
        """)

        self.conn.commit()

    def _seed_categories(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM categories")
        if cur.fetchone()["c"] > 0:
            return

        for name in DEFAULT_INCOME_CATEGORIES:
            cur.execute(
                "INSERT OR IGNORE INTO categories (name, type, icon) VALUES (?, 'income', ?)",
                (name, "💵")
            )
        for name in DEFAULT_EXPENSE_CATEGORIES:
            cur.execute(
                "INSERT OR IGNORE INTO categories (name, type, icon) VALUES (?, 'expense', ?)",
                (name, "🧾")
            )
        self.conn.commit()

    def execute(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        self.conn.commit()
        return cur

    def fetchone(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

    def fetchall(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def close(self):
        self.conn.close()
