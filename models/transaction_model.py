"""
models/transaction_model.py
Model untuk transaksi (Pemasukan & Pengeluaran).
Semua operasi CRUD terhadap tabel `transactions` ada di sini.
"""

from database.db import Database


class TransactionModel:
    def __init__(self):
        self.db = Database()

    def add(self, type_, amount, category_id, note, date):
        cur = self.db.execute(
            """INSERT INTO transactions (type, amount, category_id, note, date)
               VALUES (?, ?, ?, ?, ?)""",
            (type_, amount, category_id, note, date)
        )
        return cur.lastrowid

    def update(self, trans_id, type_, amount, category_id, note, date):
        self.db.execute(
            """UPDATE transactions
               SET type=?, amount=?, category_id=?, note=?, date=?
               WHERE id=?""",
            (type_, amount, category_id, note, date, trans_id)
        )

    def delete(self, trans_id):
        self.db.execute("DELETE FROM transactions WHERE id=?", (trans_id,))

    def get_by_id(self, trans_id):
        row = self.db.fetchone("SELECT * FROM transactions WHERE id=?", (trans_id,))
        return dict(row) if row else None

    def get_all(self, type_=None, limit=None):
        query = """
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
        """
        params = []
        if type_:
            query += " WHERE t.type = ?"
            params.append(type_)
        query += " ORDER BY t.date DESC, t.id DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        rows = self.db.fetchall(query, tuple(params))
        return [dict(r) for r in rows]

    def get_filtered(self, type_=None, category_id=None, date_from=None,
                      date_to=None, search=None):
        query = """
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []
        if type_:
            query += " AND t.type = ?"
            params.append(type_)
        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)
        if date_from:
            query += " AND t.date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND t.date <= ?"
            params.append(date_to)
        if search:
            query += " AND t.note LIKE ?"
            params.append(f"%{search}%")
        query += " ORDER BY t.date DESC, t.id DESC"
        rows = self.db.fetchall(query, tuple(params))
        return [dict(r) for r in rows]

    def get_total(self, type_, date_from=None, date_to=None):
        query = "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type=?"
        params = [type_]
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
        row = self.db.fetchone(query, tuple(params))
        return row["total"] if row else 0.0

    def get_balance(self):
        income = self.get_total("income")
        expense = self.get_total("expense")
        return income - expense

    def get_monthly_summary(self, year):
        """Mengembalikan total income & expense per bulan untuk grafik tahunan."""
        rows = self.db.fetchall(
            """SELECT strftime('%m', date) as month, type, SUM(amount) as total
               FROM transactions
               WHERE strftime('%Y', date) = ?
               GROUP BY month, type""",
            (str(year),)
        )
        summary = {str(m).zfill(2): {"income": 0.0, "expense": 0.0} for m in range(1, 13)}
        for r in rows:
            summary[r["month"]][r["type"]] = r["total"]
        return summary

    def get_category_breakdown(self, type_, date_from=None, date_to=None):
        """Total pengeluaran/pemasukan per kategori (untuk pie chart)."""
        query = """
            SELECT c.name as category_name, c.icon as category_icon,
                   COALESCE(SUM(t.amount), 0) as total
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.type = ?
        """
        params = [type_]
        if date_from:
            query += " AND t.date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND t.date <= ?"
            params.append(date_to)
        query += " GROUP BY t.category_id ORDER BY total DESC"
        rows = self.db.fetchall(query, tuple(params))
        return [dict(r) for r in rows]
