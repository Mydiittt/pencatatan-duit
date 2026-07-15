"""
views/income_expense_view.py
Halaman untuk mengelola Pemasukan atau Pengeluaran (dipakai untuk keduanya,
dibedakan lewat parameter `type_`). Berisi form tambah/edit transaksi dan
daftar transaksi dengan opsi filter, edit, dan hapus.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from config import COLORS, FONTS
from views.components import (Card, RoundedButton, GhostButton, ScrollableFrame,
                                format_currency)
from controllers.transaction_controller import TransactionController


class IncomeExpenseView(tk.Frame):
    def __init__(self, parent, app, type_="income"):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.app = app
        self.type_ = type_
        self.is_income = type_ == "income"
        self.color = COLORS["income"] if self.is_income else COLORS["expense"]
        self.color_bg = COLORS["income_bg"] if self.is_income else COLORS["expense_bg"]
        self.title_text = "Pemasukan" if self.is_income else "Pengeluaran"

        self.ctrl = TransactionController()
        self.editing_id = None

        self._build_header()
        self._build_body()
        self.refresh_list()

    # ------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["bg_main"])
        header.pack(fill="x", padx=30, pady=(26, 10))
        tk.Label(header, text=self.title_text, bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                  font=FONTS["title"]).pack(side="left")

    def _build_body(self):
        body = tk.Frame(self, bg=COLORS["bg_main"])
        body.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=3)
        body.grid_rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_list(body)

    # ------------------------------------------------------------
    def _build_form(self, parent):
        card = Card(parent, padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.form_title = tk.Label(card.inner, text=f"Tambah {self.title_text}",
                                    bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                                    font=FONTS["subtitle"])
        self.form_title.pack(anchor="w", pady=(0, 16))

        # Jumlah
        tk.Label(card.inner, text="Jumlah", bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                  font=FONTS["small"]).pack(anchor="w")
        self.amount_var = tk.StringVar()
        amount_entry = tk.Entry(card.inner, textvariable=self.amount_var, font=FONTS["body"],
                                 relief="flat", highlightthickness=1,
                                 highlightbackground=COLORS["border"], highlightcolor=self.color)
        amount_entry.pack(fill="x", pady=(4, 12), ipady=6)

        # Kategori
        tk.Label(card.inner, text="Kategori", bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                  font=FONTS["small"]).pack(anchor="w")
        self.category_var = tk.StringVar()
        self.category_map = {}
        self.category_combo = ttk.Combobox(card.inner, textvariable=self.category_var,
                                            state="readonly", font=FONTS["body"])
        self.category_combo.pack(fill="x", pady=(4, 12), ipady=4)
        self._load_categories()

        # tombol tambah kategori cepat
        add_cat_frame = tk.Frame(card.inner, bg=COLORS["bg_card"])
        add_cat_frame.pack(fill="x", pady=(0, 12))
        self.new_cat_var = tk.StringVar()
        new_cat_entry = tk.Entry(add_cat_frame, textvariable=self.new_cat_var, font=FONTS["small"],
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=COLORS["border"])
        new_cat_entry.pack(side="left", fill="x", expand=True, ipady=4)
        GhostButton(add_cat_frame, "+ Kategori", command=self._add_category,
                    fg=self.color).pack(side="left", padx=(8, 0))

        # Tanggal
        tk.Label(card.inner, text="Tanggal (YYYY-MM-DD)", bg=COLORS["bg_card"],
                  fg=COLORS["text_secondary"], font=FONTS["small"]).pack(anchor="w")
        self.date_var = tk.StringVar(value=datetime.date.today().isoformat())
        date_entry = tk.Entry(card.inner, textvariable=self.date_var, font=FONTS["body"],
                               relief="flat", highlightthickness=1,
                               highlightbackground=COLORS["border"], highlightcolor=self.color)
        date_entry.pack(fill="x", pady=(4, 12), ipady=6)

        # Catatan
        tk.Label(card.inner, text="Catatan (opsional)", bg=COLORS["bg_card"],
                  fg=COLORS["text_secondary"], font=FONTS["small"]).pack(anchor="w")
        self.note_var = tk.StringVar()
        note_entry = tk.Entry(card.inner, textvariable=self.note_var, font=FONTS["body"],
                               relief="flat", highlightthickness=1,
                               highlightbackground=COLORS["border"], highlightcolor=self.color)
        note_entry.pack(fill="x", pady=(4, 18), ipady=6)

        btn_frame = tk.Frame(card.inner, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x")
        self.submit_btn = RoundedButton(btn_frame, f"Simpan {self.title_text}",
                                         command=self._submit, bg=self.color,
                                         hover_bg=self.color)
        self.submit_btn.pack(side="left", fill="x", expand=True)
        self.cancel_btn = GhostButton(btn_frame, "Batal", command=self._cancel_edit, fg=self.color)

    def _load_categories(self):
        cats = self.ctrl.get_categories(self.type_)
        self.category_map = {f"{c['icon']} {c['name']}": c["id"] for c in cats}
        values = list(self.category_map.keys())
        self.category_combo["values"] = values
        if values:
            self.category_combo.current(0)

    def _add_category(self):
        name = self.new_cat_var.get().strip()
        if not name:
            return
        icon = "💵" if self.is_income else "🧾"
        cat_id = self.ctrl.add_category(name, self.type_, icon)
        if cat_id:
            self.new_cat_var.set("")
            self._load_categories()
            self.category_combo.set(f"{icon} {name}")
        else:
            messagebox.showinfo("Info", "Kategori sudah ada atau gagal ditambahkan.")

    def _submit(self):
        amount_str = self.amount_var.get().strip()
        date_str = self.date_var.get().strip()
        note = self.note_var.get().strip()
        cat_label = self.category_var.get()
        category_id = self.category_map.get(cat_label)

        if self.editing_id is None:
            success, errors = self.ctrl.add_transaction(
                self.type_, amount_str, category_id, note, date_str
            )
        else:
            success, errors = self.ctrl.update_transaction(
                self.editing_id, self.type_, amount_str, category_id, note, date_str
            )

        if not success:
            messagebox.showerror("Input tidak valid", "\n".join(errors))
            return

        self._cancel_edit()
        self.refresh_list()
        self.amount_var.set("")
        self.note_var.set("")
        self.date_var.set(datetime.date.today().isoformat())

    def _cancel_edit(self):
        self.editing_id = None
        self.form_title.config(text=f"Tambah {self.title_text}")
        self.submit_btn.config(text=f"Simpan {self.title_text}")
        self.cancel_btn.pack_forget()

    def _start_edit(self, t):
        self.editing_id = t["id"]
        self.form_title.config(text=f"Edit {self.title_text}")
        self.submit_btn.config(text="Simpan Perubahan")
        self.cancel_btn.pack(side="left", padx=(8, 0))

        self.amount_var.set(str(t["amount"]))
        self.date_var.set(t["date"])
        self.note_var.set(t.get("note") or "")
        for label, cid in self.category_map.items():
            if cid == t.get("category_id"):
                self.category_combo.set(label)
                break

    # ------------------------------------------------------------
    def _build_list(self, parent):
        card = Card(parent, padding=18)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        header = tk.Frame(card.inner, bg=COLORS["bg_card"])
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text=f"Riwayat {self.title_text}", bg=COLORS["bg_card"],
                  fg=COLORS["text_primary"], font=FONTS["subtitle"]).pack(side="left")

        self.total_label = tk.Label(header, text="", bg=COLORS["bg_card"], fg=self.color,
                                     font=FONTS["body_bold"])
        self.total_label.pack(side="right")

        self.list_container = ScrollableFrame(card.inner, bg=COLORS["bg_card"])
        self.list_container.pack(fill="both", expand=True)

    def refresh_list(self):
        for w in self.list_container.scrollable_frame.winfo_children():
            w.destroy()

        transactions = self.ctrl.list_transactions(type_=self.type_)
        total = sum(t["amount"] for t in transactions)
        self.total_label.config(text=format_currency(total))

        if not transactions:
            tk.Label(self.list_container.scrollable_frame,
                      text=f"Belum ada data {self.title_text.lower()}.",
                      bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                      font=FONTS["body"]).pack(pady=30)
            return

        for t in transactions:
            self._build_row(t)

    def _build_row(self, t):
        parent = self.list_container.scrollable_frame
        row = tk.Frame(parent, bg=COLORS["bg_card_alt"])
        row.pack(fill="x", pady=4, padx=2)

        inner = tk.Frame(row, bg=COLORS["bg_card_alt"])
        inner.pack(fill="x", padx=12, pady=10)

        icon = t.get("category_icon") or ("💵" if self.is_income else "🧾")
        tk.Label(inner, text=icon, bg=self.color_bg, fg=self.color, font=("Segoe UI", 12),
                  width=3).pack(side="left", padx=(0, 10))

        info = tk.Frame(inner, bg=COLORS["bg_card_alt"])
        info.pack(side="left", fill="x", expand=True)
        cat_name = t.get("category_name") or "Tanpa kategori"
        tk.Label(info, text=cat_name, bg=COLORS["bg_card_alt"], fg=COLORS["text_primary"],
                  font=FONTS["body_bold"], anchor="w").pack(fill="x")
        note = t.get("note") or ""
        subtitle = t["date"] + (f" • {note}" if note else "")
        tk.Label(info, text=subtitle, bg=COLORS["bg_card_alt"], fg=COLORS["text_secondary"],
                  font=FONTS["small"], anchor="w").pack(fill="x")

        right = tk.Frame(inner, bg=COLORS["bg_card_alt"])
        right.pack(side="right")
        tk.Label(right, text=format_currency(t["amount"]), bg=COLORS["bg_card_alt"],
                  fg=self.color, font=FONTS["body_bold"]).pack(anchor="e")

        actions = tk.Frame(right, bg=COLORS["bg_card_alt"])
        actions.pack(anchor="e", pady=(4, 0))
        tk.Label(actions, text="Edit", bg=COLORS["bg_card_alt"], fg=COLORS["accent"],
                  font=FONTS["small"], cursor="hand2").pack(side="left", padx=(0, 8))
        tk.Label(actions, text="Hapus", bg=COLORS["bg_card_alt"], fg=COLORS["expense"],
                  font=FONTS["small"], cursor="hand2").pack(side="left")

        for widget in actions.winfo_children():
            if widget.cget("text") == "Edit":
                widget.bind("<Button-1>", lambda e, tr=t: self._start_edit(tr))
            else:
                widget.bind("<Button-1>", lambda e, tr=t: self._delete(tr))

    def _delete(self, t):
        if messagebox.askyesno("Konfirmasi", f"Hapus transaksi ini ({format_currency(t['amount'])})?"):
            self.ctrl.delete_transaction(t["id"])
            self.refresh_list()
