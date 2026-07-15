"""
views/dashboard_view.py
Halaman utama (Dashboard): menampilkan ringkasan saldo, total pemasukan,
total pengeluaran bulan ini, grafik tren singkat, dan transaksi terbaru.
"""

import tkinter as tk
import datetime
from config import COLORS, FONTS
from views.components import StatCard, Card, format_currency, RoundedButton
from controllers.transaction_controller import TransactionController
from controllers.report_controller import ReportController


class DashboardView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.app = app
        self.trans_ctrl = TransactionController()
        self.report_ctrl = ReportController()

        self._build_header()
        self._build_stat_cards()
        self._build_body()

    # ------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["bg_main"])
        header.pack(fill="x", padx=30, pady=(26, 10))

        today = datetime.date.today()
        tk.Label(header, text="Dashboard", bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                  font=FONTS["title"]).pack(side="left")
        tk.Label(header, text=f"  •  {today.strftime('%d %B %Y')}", bg=COLORS["bg_main"],
                  fg=COLORS["text_secondary"], font=FONTS["body"]).pack(side="left")

    def _build_stat_cards(self):
        wrap = tk.Frame(self, bg=COLORS["bg_main"])
        wrap.pack(fill="x", padx=30, pady=10)

        today = datetime.date.today()
        month_start = today.replace(day=1).isoformat()
        month_end = today.isoformat()

        balance = self.trans_ctrl.get_balance()
        income_month = self.trans_ctrl.get_total_income(month_start, month_end)
        expense_month = self.trans_ctrl.get_total_expense(month_start, month_end)

        for i in range(3):
            wrap.grid_columnconfigure(i, weight=1, uniform="stat")

        StatCard(wrap, "Saldo Total", format_currency(balance), COLORS["accent"], "💼").grid(
            row=0, column=0, sticky="nsew", padx=(0, 10))
        StatCard(wrap, "Pemasukan Bulan Ini", format_currency(income_month), COLORS["income"], "⬆️").grid(
            row=0, column=1, sticky="nsew", padx=10)
        StatCard(wrap, "Pengeluaran Bulan Ini", format_currency(expense_month), COLORS["expense"], "⬇️").grid(
            row=0, column=2, sticky="nsew", padx=(10, 0))

    def _build_body(self):
        body = tk.Frame(self, bg=COLORS["bg_main"])
        body.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        self._build_trend_chart(body)
        self._build_recent_transactions(body)

    # ------------------------------------------------------------
    def _build_trend_chart(self, parent):
        card = Card(parent, padding=18)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(card.inner, text="Tren 6 Bulan Terakhir", bg=COLORS["bg_card"],
                  fg=COLORS["text_primary"], font=FONTS["subtitle"]).pack(anchor="w", pady=(0, 14))

        canvas = tk.Canvas(card.inner, bg=COLORS["bg_card"], highlightthickness=0, height=280)
        canvas.pack(fill="both", expand=True)
        canvas.bind("<Configure>", lambda e: self._draw_trend(canvas))
        self._trend_canvas = canvas

    def _draw_trend(self, canvas):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10 or h < 10:
            return

        today = datetime.date.today()
        months = []
        for i in range(5, -1, -1):
            m = today.month - i
            y = today.year
            while m <= 0:
                m += 12
                y -= 1
            months.append((y, m))

        data = []
        for y, m in months:
            summary = self.report_ctrl.get_month_summary(m, y)
            data.append(summary)

        max_val = max([max(d["income"], d["expense"]) for d in data] + [1])
        padding_left = 60
        padding_bottom = 30
        padding_top = 20
        chart_w = w - padding_left - 20
        chart_h = h - padding_bottom - padding_top
        n = len(data)
        group_w = chart_w / n

        # gridlines
        for i in range(4):
            y = padding_top + chart_h - (chart_h * i / 3)
            canvas.create_line(padding_left, y, w - 20, y, fill=COLORS["border"])
            val = max_val * i / 3
            canvas.create_text(padding_left - 10, y, text=f"{val/1000:.0f}rb" if val < 1_000_000 else f"{val/1_000_000:.1f}jt",
                                fill=COLORS["text_secondary"], font=FONTS["small"], anchor="e")

        bar_w = group_w * 0.28
        for idx, (d, (y, m)) in enumerate(zip(data, months)):
            gx = padding_left + idx * group_w + group_w / 2
            inc_h = (d["income"] / max_val) * chart_h if max_val else 0
            exp_h = (d["expense"] / max_val) * chart_h if max_val else 0

            x1 = gx - bar_w - 3
            canvas.create_rectangle(x1, padding_top + chart_h - inc_h, x1 + bar_w,
                                     padding_top + chart_h, fill=COLORS["income"], outline="")
            x2 = gx + 3
            canvas.create_rectangle(x2, padding_top + chart_h - exp_h, x2 + bar_w,
                                     padding_top + chart_h, fill=COLORS["expense"], outline="")

            label = f"{['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'][m-1]}"
            canvas.create_text(gx, padding_top + chart_h + 14, text=label,
                                fill=COLORS["text_secondary"], font=FONTS["small"])

        # legend
        canvas.create_rectangle(w - 160, 4, w - 148, 16, fill=COLORS["income"], outline="")
        canvas.create_text(w - 142, 10, text="Pemasukan", fill=COLORS["text_secondary"],
                            font=FONTS["small"], anchor="w")
        canvas.create_rectangle(w - 70, 4, w - 58, 16, fill=COLORS["expense"], outline="")
        canvas.create_text(w - 52, 10, text="Pengeluaran", fill=COLORS["text_secondary"],
                            font=FONTS["small"], anchor="w")

    # ------------------------------------------------------------
    def _build_recent_transactions(self, parent):
        card = Card(parent, padding=18)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        header = tk.Frame(card.inner, bg=COLORS["bg_card"])
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Transaksi Terbaru", bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                  font=FONTS["subtitle"]).pack(side="left")

        recent = self.report_ctrl.get_recent_transactions(limit=8)

        if not recent:
            tk.Label(card.inner, text="Belum ada transaksi.\nMulai catat pemasukan atau pengeluaran Anda!",
                      bg=COLORS["bg_card"], fg=COLORS["text_secondary"], font=FONTS["body"],
                      justify="left").pack(anchor="w", pady=20)
            return

        for t in recent:
            self._build_transaction_row(card.inner, t)

    def _build_transaction_row(self, parent, t):
        row = tk.Frame(parent, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=6)

        is_income = t["type"] == "income"
        color = COLORS["income"] if is_income else COLORS["expense"]
        bg_badge = COLORS["income_bg"] if is_income else COLORS["expense_bg"]
        icon = t.get("category_icon") or ("💵" if is_income else "🧾")

        icon_lbl = tk.Label(row, text=icon, bg=bg_badge, fg=color, font=("Segoe UI", 12),
                              width=3, height=1)
        icon_lbl.pack(side="left", padx=(0, 10))

        info = tk.Frame(row, bg=COLORS["bg_card"])
        info.pack(side="left", fill="x", expand=True)
        cat_name = t.get("category_name") or "Tanpa kategori"
        tk.Label(info, text=cat_name, bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                  font=FONTS["body_bold"], anchor="w").pack(fill="x")
        date_str = t["date"]
        note = t.get("note") or ""
        subtitle = f"{date_str}" + (f" • {note}" if note else "")
        tk.Label(info, text=subtitle, bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                  font=FONTS["small"], anchor="w").pack(fill="x")

        sign = "+" if is_income else "-"
        tk.Label(row, text=f"{sign} {format_currency(t['amount'])}", bg=COLORS["bg_card"],
                  fg=color, font=FONTS["body_bold"]).pack(side="right")
