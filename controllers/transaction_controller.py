"""
controllers/transaction_controller.py
Menjembatani View dengan Model untuk operasi transaksi (pemasukan & pengeluaran).
Melakukan validasi input sebelum diteruskan ke Model.
"""

from models.transaction_model import TransactionModel
from models.category_model import CategoryModel


class TransactionController:
    def __init__(self):
        self.model = TransactionModel()
        self.category_model = CategoryModel()

    # ---------- Validasi ----------
    def validate(self, amount_str, date_str):
        errors = []
        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append("Jumlah harus lebih besar dari 0.")
        except (ValueError, TypeError):
            errors.append("Jumlah harus berupa angka yang valid.")
            amount = None

        if not date_str:
            errors.append("Tanggal wajib diisi.")

        return errors, amount

    # ---------- CRUD ----------
    def add_transaction(self, type_, amount_str, category_id, note, date_str):
        errors, amount = self.validate(amount_str, date_str)
        if errors:
            return False, errors
        self.model.add(type_, amount, category_id, note.strip(), date_str)
        return True, []

    def update_transaction(self, trans_id, type_, amount_str, category_id, note, date_str):
        errors, amount = self.validate(amount_str, date_str)
        if errors:
            return False, errors
        self.model.update(trans_id, type_, amount, category_id, note.strip(), date_str)
        return True, []

    def delete_transaction(self, trans_id):
        self.model.delete(trans_id)
        return True

    def get_transaction(self, trans_id):
        return self.model.get_by_id(trans_id)

    def list_transactions(self, type_=None, limit=None):
        return self.model.get_all(type_=type_, limit=limit)

    def filter_transactions(self, **kwargs):
        return self.model.get_filtered(**kwargs)

    # ---------- Kategori ----------
    def get_categories(self, type_):
        return self.category_model.get_all(type_)

    def add_category(self, name, type_, icon="💰"):
        return self.category_model.add(name, type_, icon)

    def delete_category(self, category_id):
        self.category_model.delete(category_id)

    # ---------- Ringkasan ----------
    def get_balance(self):
        return self.model.get_balance()

    def get_total_income(self, date_from=None, date_to=None):
        return self.model.get_total("income", date_from, date_to)

    def get_total_expense(self, date_from=None, date_to=None):
        return self.model.get_total("expense", date_from, date_to)
