"""
models/category_model.py
Model untuk mengelola data kategori (income/expense).
"""

from database.db import Database


class CategoryModel:
    def __init__(self):
        self.db = Database()

    def get_all(self, type_=None):
        if type_:
            rows = self.db.fetchall(
                "SELECT * FROM categories WHERE type = ? ORDER BY name", (type_,)
            )
        else:
            rows = self.db.fetchall("SELECT * FROM categories ORDER BY type, name")
        return [dict(r) for r in rows]

    def get_by_id(self, category_id):
        row = self.db.fetchone("SELECT * FROM categories WHERE id = ?", (category_id,))
        return dict(row) if row else None

    def add(self, name, type_, icon="💰"):
        try:
            cur = self.db.execute(
                "INSERT INTO categories (name, type, icon) VALUES (?, ?, ?)",
                (name.strip(), type_, icon)
            )
            return cur.lastrowid
        except Exception:
            return None

    def delete(self, category_id):
        self.db.execute("DELETE FROM categories WHERE id = ?", (category_id,))

    def rename(self, category_id, new_name):
        self.db.execute(
            "UPDATE categories SET name = ? WHERE id = ?", (new_name.strip(), category_id)
        )
