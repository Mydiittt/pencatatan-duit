"""
views/budget_view.py
Halaman Penganggaran (Budgeting): pengguna mengatur batas anggaran per kategori
pengeluaran untuk bulan tertentu, dan melihat progres realisasinya.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from config import COLORS, FONTS
from views.components import Card, RoundedButton, ScrollableFrame, format_currency, make_progress_bar
from controllers.budget_controller import BudgetController

MONTH_NAMES = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
               "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


class BudgetView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.app = app
        self.ctrl = BudgetController()

        today = datetime.date.today()
        self.month = today.month
        self.year = today.year

        self._build_header()
        self._build_body()
        self.refresh()

    # ------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["bg_main"])
        header.pack(fill="x", padx=30, pady=(26, 10))
        tk.Label(header, text="Penganggaran", bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                  font=FONTS["title"]).pack(side="left")

        nav = tk.Frame(header, bg=COLORS["bg_main"])
        nav.pack(side="right")
        prev_lbl = tk.Label(nav, text="◀", bg=COLORS["bg_main"], fg=COLORS["accent"],
                             font=FONTS["subtitle"], cursor="hand2")
        prev_lbl.pack(side="left", padx=8)
        prev_lbl.bind("<Button-1>", lambda e: self._change_month(-1))
        self.month_label = tk.Label(nav, text="", bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                                     font=FONTS["subtitle"])
        self.month_label.pack(side="left", padx=8)
        next_lbl = tk.Label(nav, text="▶", bg=COLORS["bg_main"], fg=COLORS["accent"],
                              font=FONTS["subtitle"], cursor="hand2")
        next_lbl.pack(side="left", padx=8)
        next_lbl.bind("<Button-1>", lambda e: self._change_month(1))

    def _change_month(self, delta):
        self.month += delta
        if self.month > 12:
            self.month = 1
            self.year += 1
        elif self.month < 1:
            self.month = 12
            self.year -= 1
        self.refresh()

    def _build_body(self):
        body = tk.Frame(self, bg=COLORS["bg_main"])
        body.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=3)
        body.grid_rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_list(body)

    def _build_form(self, parent):
        card = Card(parent, padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(card.inner, text="Atur Anggaran Baru", bg=COLORS["bg_card"],
                  fg=COLORS["text_primary"], font=FONTS["subtitle"]).pack(anchor="w", pady=(0, 16))

        tk.Label(card.inner, text="Kategori Pengeluaran", bg=COLORS["bg_card"],
                  fg=COLORS["text_secondary"], font=FONTS["small"]).pack(anchor="w")
        self.category_var = tk.StringVar()
        self.category_map = {}
        self.category_combo = ttk.Combobox(card.inner, textvariable=self.category_var,
                                            state="readonly", font=FONTS["body"])
        self.category_combo.pack(fill="x", pady=(4, 12), ipady=4)
        self._load_categories()

        tk.Label(card.inner, text="Jumlah Anggaran", bg=COLORS["bg_card"],
                  fg=COLORS["text_secondary"], font=FONTS["small"]).pack(anchor="w")
        self.amount_var = tk.StringVar()
        amount_entry = tk.Entry(card.inner, textvariable=self.amount_var, font=FONTS["body"],
                                 relief="flat", highlightthickness=1,
                                 highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"])
        amount_entry.pack(fill="x", pady=(4, 20), ipady=6)

        RoundedButton(card.inner, "Simpan Anggaran", command=self._submit).pack(fill="x")

        tk.Label(card.inner, text="Anggaran berlaku untuk bulan yang sedang ditampilkan.\n"
                                    "Anda bisa mengaturnya per kategori setiap bulan.",
                  bg=COLORS["bg_card"], fg=COLORS["text_secondary"], font=FONTS["small"],
                  justify="left", wraplength=280).pack(anchor="w", pady=(16, 0))

    def _load_categories(self):
        cats = self.ctrl.get_expense_categories()
        self.category_map = {f"{c['icon']} {c['name']}": c["id"] for c in cats}
        values = list(self.category_map.keys())
        self.category_combo["values"] = values
        if values:
            self.category_combo.current(0)

    def _submit(self):
        cat_label = self.category_var.get()
        category_id = self.category_map.get(cat_label)
        amount_str = self.amount_var.get().strip()

        if not category_id:
            messagebox.showerror("Error", "Silakan pilih kategori.")
            return

        success, errors = self.ctrl.set_budget(category_id, amount_str, self.month, self.year)
        if not success:
            messagebox.showerror("Input tidak valid", "\n".join(errors))
            return

        self.amount_var.set("")
        self.refresh()

    def _build_list(self, parent):
        card = Card(parent, padding=18)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(card.inner, text="Progres Anggaran", bg=COLORS["bg_card"],
                  fg=COLORS["text_primary"], font=FONTS["subtitle"]).pack(anchor="w", pady=(0, 10))

        self.list_container = ScrollableFrame(card.inner, bg=COLORS["bg_card"])
        self.list_container.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    def refresh(self):
        self.month_label.config(text=f"{MONTH_NAMES[self.month - 1]} {self.year}")

        for w in self.list_container.scrollable_frame.winfo_children():
            w.destroy()

        budgets = self.ctrl.get_budgets_with_usage(self.month, self.year)

        if not budgets:
            tk.Label(self.list_container.scrollable_frame,
                      text="Belum ada anggaran untuk bulan ini.\nTambahkan anggaran di sebelah kiri.",
                      bg=COLORS["bg_card"], fg=COLORS["text_secondary"], font=FONTS["body"],
                      justify="left").pack(pady=30)
            return

        for b in budgets:
            self._build_budget_row(b)

    def _build_budget_row(self, b):
        parent = self.list_container.scrollable_frame
        row = tk.Frame(parent, bg=COLORS["bg_card_alt"])
        row.pack(fill="x", pady=6, padx=2)

        inner = tk.Frame(row, bg=COLORS["bg_card_alt"])
        inner.pack(fill="x", padx=14, pady=12)

        top = tk.Frame(inner, bg=COLORS["bg_card_alt"])
        top.pack(fill="x")
        tk.Label(top, text=f"{b['category_icon']} {b['category_name']}", bg=COLORS["bg_card_alt"],
                  fg=COLORS["text_primary"], font=FONTS["body_bold"]).pack(side="left")

        percent = b["percent"]
        if percent >= 100:
            status_color = COLORS["expense"]
            status_text = "Melebihi anggaran!"
        elif percent >= 80:
            status_color = COLORS["warning"]
            status_text = "Mendekati batas"
        else:
            status_color = COLORS["income"]
            status_text = "Aman"

        tk.Label(top, text=status_text, bg=COLORS["bg_card_alt"], fg=status_color,
                  font=FONTS["small"]).pack(side="right")

        mid = tk.Frame(inner, bg=COLORS["bg_card_alt"])
        mid.pack(fill="x", pady=(8, 4))
        tk.Label(mid, text=f"{format_currency(b['spent'])} dari {format_currency(b['amount'])}",
                  bg=COLORS["bg_card_alt"], fg=COLORS["text_secondary"],
                  font=FONTS["small"]).pack(side="left")
        tk.Label(mid, text=f"{percent:.0f}%", bg=COLORS["bg_card_alt"], fg=status_color,
                  font=FONTS["small"]).pack(side="right")

        bar = make_progress_bar(inner, percent, status_color, bg=COLORS["border"], width=400, height=10)
        bar.pack(fill="x", pady=(2, 4))

        del_lbl = tk.Label(inner, text="Hapus anggaran", bg=COLORS["bg_card_alt"], fg=COLORS["expense"],
                            font=FONTS["small"], cursor="hand2")
        del_lbl.pack(anchor="e", pady=(4, 0))
        del_lbl.bind("<Button-1>", lambda e, bid=b["id"]: self._delete_budget(bid))

    def _delete_budget(self, budget_id):
        if messagebox.askyesno("Konfirmasi", "Hapus anggaran ini?"):
            self.ctrl.delete_budget(budget_id)
            self.refresh()
