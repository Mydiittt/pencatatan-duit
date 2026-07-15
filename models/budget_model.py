"""
models/budget_model.py
Model untuk penganggaran (budgeting) per kategori per bulan.
"""

from database.db import Database


class BudgetModel:
    def __init__(self):
        self.db = Database()

    def set_budget(self, category_id, amount, month, year):
        existing = self.db.fetchone(
            "SELECT id FROM budgets WHERE category_id=? AND month=? AND year=?",
            (category_id, month, year)
        )
        if existing:
            self.db.execute(
                "UPDATE budgets SET amount=? WHERE id=?", (amount, existing["id"])
            )
            return existing["id"]
        else:
            cur = self.db.execute(
                "INSERT INTO budgets (category_id, amount, month, year) VALUES (?, ?, ?, ?)",
                (category_id, amount, month, year)
            )
            return cur.lastrowid

    def delete_budget(self, budget_id):
        self.db.execute("DELETE FROM budgets WHERE id=?", (budget_id,))

    def get_budgets(self, month, year):
        rows = self.db.fetchall(
            """SELECT b.*, c.name as category_name, c.icon as category_icon
               FROM budgets b
               JOIN categories c ON b.category_id = c.id
               WHERE b.month=? AND b.year=?
               ORDER BY c.name""",
            (month, year)
        )
        return [dict(r) for r in rows]

    def get_budget_with_usage(self, month, year):
        """Menggabungkan data budget dengan realisasi pengeluaran bulan tsb."""
        budgets = self.get_budgets(month, year)
        date_from = f"{year:04d}-{month:02d}-01"
        if month == 12:
            next_month_year = year + 1
            next_month = 1
        else:
            next_month_year = year
            next_month = month + 1
        date_to = f"{next_month_year:04d}-{next_month:02d}-01"

        result = []
        for b in budgets:
            row = self.db.fetchone(
                """SELECT COALESCE(SUM(amount),0) as spent FROM transactions
                   WHERE type='expense' AND category_id=? AND date >= ? AND date < ?""",
                (b["category_id"], date_from, date_to)
            )
            spent = row["spent"] if row else 0.0
            b["spent"] = spent
            b["remaining"] = b["amount"] - spent
            b["percent"] = (spent / b["amount"] * 100) if b["amount"] > 0 else 0
            result.append(b)
        return result
