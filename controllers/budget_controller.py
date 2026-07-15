"""
controllers/budget_controller.py
Menjembatani View dengan Model untuk fitur penganggaran (budgeting).
"""

from models.budget_model import BudgetModel
from models.category_model import CategoryModel


class BudgetController:
    def __init__(self):
        self.model = BudgetModel()
        self.category_model = CategoryModel()

    def validate(self, amount_str):
        errors = []
        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append("Jumlah anggaran harus lebih besar dari 0.")
        except (ValueError, TypeError):
            errors.append("Jumlah anggaran harus berupa angka yang valid.")
            amount = None
        return errors, amount

    def set_budget(self, category_id, amount_str, month, year):
        errors, amount = self.validate(amount_str)
        if errors:
            return False, errors
        self.model.set_budget(category_id, amount, month, year)
        return True, []

    def delete_budget(self, budget_id):
        self.model.delete_budget(budget_id)

    def get_budgets_with_usage(self, month, year):
        return self.model.get_budget_with_usage(month, year)

    def get_expense_categories(self):
        return self.category_model.get_all("expense")
