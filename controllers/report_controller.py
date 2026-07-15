"""
controllers/report_controller.py
Menyediakan data yang sudah diolah untuk halaman Analisis & Laporan.
"""

import calendar
from models.transaction_model import TransactionModel


class ReportController:
    def __init__(self):
        self.model = TransactionModel()

    def month_range(self, month, year):
        date_from = f"{year:04d}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        date_to = f"{year:04d}-{month:02d}-{last_day:02d}"
        return date_from, date_to

    def get_month_summary(self, month, year):
        date_from, date_to = self.month_range(month, year)
        income = self.model.get_total("income", date_from, date_to)
        expense = self.model.get_total("expense", date_from, date_to)
        return {
            "income": income,
            "expense": expense,
            "net": income - expense,
        }

    def get_category_breakdown(self, type_, month, year):
        date_from, date_to = self.month_range(month, year)
        return self.model.get_category_breakdown(type_, date_from, date_to)

    def get_yearly_trend(self, year):
        return self.model.get_monthly_summary(year)

    def get_recent_transactions(self, limit=8):
        return self.model.get_all(limit=limit)
