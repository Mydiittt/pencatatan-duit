"""
views/report_view.py
Halaman Analisis & Laporan: menampilkan ringkasan bulanan, grafik pie
kategori pengeluaran/pemasukan, dan tren tahunan.
"""

import tkinter as tk
from tkinter import ttk
import math
import datetime

from config import COLORS, FONTS
from views.components import Card, format_currency
from controllers.report_controller import ReportController

MONTH_NAMES = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
               "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


class ReportView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.app = app
        self.ctrl = ReportController()

        today = datetime.date.today()
        self.month = today.month
        self.year = today.year
        self.report_type = "expense"

        self._build_header()
        self._build_body()
        self.refresh()

    # ------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["bg_main"])
        header.pack(fill="x", padx=30, pady=(26, 10))
        tk.Label(header, text="Analisis & Laporan", bg=COLORS["bg_main"], fg=COLORS["text_primary"],
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
        # summary strip
        self.summary_frame = tk.Frame(self, bg=COLORS["bg_main"])
        self.summary_frame.pack(fill="x", padx=30, pady=(0, 10))

        body = tk.Frame(self, bg=COLORS["bg_main"])
        body.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self._build_pie_card(body)
        self._build_breakdown_card(body)

    def _build_pie_card(self, parent):
        card = Card(parent, padding=18)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        top = tk.Frame(card.inner, bg=COLORS["bg_card"])
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text="Komposisi per Kategori", bg=COLORS["bg_card"],
                  fg=COLORS["text_primary"], font=FONTS["subtitle"]).pack(side="left")

        toggle = tk.Frame(top, bg=COLORS["bg_card"])
        toggle.pack(side="right")
        self.expense_toggle = tk.Label(toggle, text="Pengeluaran", bg=COLORS["expense"],
                                        fg=COLORS["text_light"], font=FONTS["small"], padx=10, pady=4,
                                        cursor="hand2")
        self.expense_toggle.pack(side="left")
        self.income_toggle = tk.Label(toggle, text="Pemasukan", bg=COLORS["bg_card_alt"],
                                       fg=COLORS["text_secondary"], font=FONTS["small"], padx=10, pady=4,
                                       cursor="hand2")
        self.income_toggle.pack(side="left", padx=(4, 0))
        self.expense_toggle.bind("<Button-1>", lambda e: self._set_report_type("expense"))
        self.income_toggle.bind("<Button-1>", lambda e: self._set_report_type("income"))

        self.pie_canvas = tk.Canvas(card.inner, bg=COLORS["bg_card"], highlightthickness=0, height=300)
        self.pie_canvas.pack(fill="both", expand=True)
        self.pie_canvas.bind("<Configure>", lambda e: self._draw_pie())

    def _set_report_type(self, type_):
        self.report_type = type_
        if type_ == "expense":
            self.expense_toggle.config(bg=COLORS["expense"], fg=COLORS["text_light"])
            self.income_toggle.config(bg=COLORS["bg_card_alt"], fg=COLORS["text_secondary"])
        else:
            self.income_toggle.config(bg=COLORS["income"], fg=COLORS["text_light"])
            self.expense_toggle.config(bg=COLORS["bg_card_alt"], fg=COLORS["text_secondary"])
        self.refresh()

    def _build_breakdown_card(self, parent):
        card = Card(parent, padding=18)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(card.inner, text="Rincian Kategori", bg=COLORS["bg_card"],
                  fg=COLORS["text_primary"], font=FONTS["subtitle"]).pack(anchor="w", pady=(0, 10))

        self.breakdown_frame = tk.Frame(card.inner, bg=COLORS["bg_card"])
        self.breakdown_frame.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    def refresh(self):
        self.month_label.config(text=f"{MONTH_NAMES[self.month - 1]} {self.year}")
        self._build_summary_strip()
        self._draw_pie()
        self._build_breakdown()

    def _build_summary_strip(self):
        for w in self.summary_frame.winfo_children():
            w.destroy()

        summary = self.ctrl.get_month_summary(self.month, self.year)
        items = [
            ("Pemasukan", summary["income"], COLORS["income"]),
            ("Pengeluaran", summary["expense"], COLORS["expense"]),
            ("Selisih (Net)", summary["net"], COLORS["accent"] if summary["net"] >= 0 else COLORS["expense"]),
        ]
        for i, (label, val, color) in enumerate(items):
            box = tk.Frame(self.summary_frame, bg=COLORS["bg_card"], highlightbackground=COLORS["border"],
                            highlightthickness=1)
            box.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else 8, 0))
            inner = tk.Frame(box, bg=COLORS["bg_card"])
            inner.pack(fill="both", padx=16, pady=10)
            tk.Label(inner, text=label, bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                      font=FONTS["small"]).pack(anchor="w")
            tk.Label(inner, text=format_currency(val), bg=COLORS["bg_card"], fg=color,
                      font=FONTS["subtitle"]).pack(anchor="w")

    def _draw_pie(self):
        canvas = self.pie_canvas
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 20 or h < 20:
            return

        data = self.ctrl.get_category_breakdown(self.report_type, self.month, self.year)
        data = [d for d in data if d["total"] > 0]
        total = sum(d["total"] for d in data)

        cx, cy = w * 0.35, h / 2
        radius = min(w * 0.3, h / 2 - 20)

        if not data or total == 0:
            canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                fill=COLORS["bg_card_alt"], outline="")
            canvas.create_text(cx, cy, text="Belum ada\ndata", fill=COLORS["text_secondary"],
                                font=FONTS["body"], justify="center")
            return

        colors = COLORS["chart_colors"]
        start_angle = 0
        legend_x = w * 0.62
        legend_y = 20

        for i, d in enumerate(data):
            extent = (d["total"] / total) * 360
            color = colors[i % len(colors)]
            canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius,
                               start=start_angle, extent=extent, fill=color, outline=COLORS["bg_card"], width=2)
            start_angle += extent

            if legend_y < h - 20 and i < 8:
                canvas.create_rectangle(legend_x, legend_y, legend_x + 12, legend_y + 12,
                                          fill=color, outline="")
                pct = d["total"] / total * 100
                name = d["category_name"] or "Lainnya"
                if len(name) > 16:
                    name = name[:15] + "…"
                canvas.create_text(legend_x + 18, legend_y + 6, text=f"{name} ({pct:.0f}%)",
                                    fill=COLORS["text_primary"], font=FONTS["small"], anchor="w")
                legend_y += 22

        canvas.create_oval(cx - radius * 0.55, cy - radius * 0.55, cx + radius * 0.55, cy + radius * 0.55,
                            fill=COLORS["bg_card"], outline="")
        canvas.create_text(cx, cy, text=format_currency(total), fill=COLORS["text_primary"],
                            font=FONTS["small"], justify="center", width=int(radius * 1.1))

    def _build_breakdown(self):
        for w in self.breakdown_frame.winfo_children():
            w.destroy()

        data = self.ctrl.get_category_breakdown(self.report_type, self.month, self.year)
        data = [d for d in data if d["total"] > 0]
        total = sum(d["total"] for d in data)

        if not data:
            tk.Label(self.breakdown_frame, text="Belum ada data untuk bulan ini.",
                      bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                      font=FONTS["body"]).pack(pady=20)
            return

        colors = COLORS["chart_colors"]
        for i, d in enumerate(data):
            row = tk.Frame(self.breakdown_frame, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=6)

            color = colors[i % len(colors)]
            tk.Frame(row, bg=color, width=4).pack(side="left", fill="y", padx=(0, 10))

            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)
            name = d["category_name"] or "Lainnya"
            icon = d.get("category_icon") or "💰"
            tk.Label(info, text=f"{icon} {name}", bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                      font=FONTS["body_bold"], anchor="w").pack(fill="x")

            pct = (d["total"] / total * 100) if total else 0
            tk.Label(info, text=f"{pct:.1f}% dari total", bg=COLORS["bg_card"],
                      fg=COLORS["text_secondary"], font=FONTS["small"], anchor="w").pack(fill="x")

            tk.Label(row, text=format_currency(d["total"]), bg=COLORS["bg_card"],
                      fg=COLORS["text_primary"], font=FONTS["body_bold"]).pack(side="right")
