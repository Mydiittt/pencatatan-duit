"""
views/main_view.py
Jendela utama aplikasi: menyediakan sidebar navigasi dan area konten
yang berganti-ganti tergantung menu yang dipilih (Dashboard, Pemasukan,
Pengeluaran, Penganggaran, Laporan).
"""

import tkinter as tk
from config import COLORS, FONTS, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT

from views.dashboard_view import DashboardView
from views.income_expense_view import IncomeExpenseView
from views.budget_view import BudgetView
from views.report_view import ReportView


class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — Kelola Keuangan Pribadi")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(bg=COLORS["bg_main"])

        self.nav_buttons = {}
        self.current_view = None
        self.views = {}

        self._build_layout()
        self._build_sidebar()
        self.show_view("dashboard")

    # ---------------------------------------------------------------
    def _build_layout(self):
        self.sidebar = tk.Frame(self, bg=COLORS["bg_sidebar"], width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg=COLORS["bg_main"])
        self.content.pack(side="right", fill="both", expand=True)

    def _build_sidebar(self):
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        logo_frame.pack(fill="x", pady=(28, 8), padx=20)
        tk.Label(logo_frame, text="💰", bg=COLORS["bg_sidebar"],
                  font=("Segoe UI", 22)).pack(side="left")
        tk.Label(logo_frame, text=APP_NAME, bg=COLORS["bg_sidebar"], fg=COLORS["text_light"],
                  font=("Segoe UI", 16, "bold")).pack(side="left", padx=(8, 0))

        tk.Frame(self.sidebar, bg=COLORS["bg_sidebar_hover"], height=1).pack(fill="x", padx=20, pady=(10, 20))

        menu_items = [
            ("dashboard", "🏠", "Dashboard"),
            ("income", "⬆️", "Pemasukan"),
            ("expense", "⬇️", "Pengeluaran"),
            ("budget", "🎯", "Penganggaran"),
            ("report", "📊", "Analisis & Laporan"),
        ]

        for key, icon, label in menu_items:
            self._add_nav_button(key, icon, label)

        # footer
        footer = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        footer.pack(side="bottom", fill="x", pady=20, padx=20)
        tk.Label(footer, text="Kelola keuangan\ndengan lebih cerdas.", bg=COLORS["bg_sidebar"],
                  fg=COLORS["text_secondary"], font=FONTS["small"], justify="left").pack(anchor="w")

    def _add_nav_button(self, key, icon, label):
        btn_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        btn_frame.pack(fill="x", padx=12, pady=3)

        btn = tk.Label(btn_frame, text=f"  {icon}   {label}", bg=COLORS["bg_sidebar"],
                        fg=COLORS["text_secondary"], font=FONTS["sidebar"], anchor="w",
                        padx=10, pady=10, cursor="hand2")
        btn.pack(fill="x")
        btn.bind("<Button-1>", lambda e, k=key: self.show_view(k))
        btn.bind("<Enter>", lambda e, b=btn, k=key: self._on_hover(b, k, True))
        btn.bind("<Leave>", lambda e, b=btn, k=key: self._on_hover(b, k, False))

        self.nav_buttons[key] = btn

    def _on_hover(self, btn, key, entering):
        if self.current_view == key:
            return
        if entering:
            btn.config(bg=COLORS["bg_sidebar_hover"], fg=COLORS["text_light"])
        else:
            btn.config(bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"])

    def _update_nav_selection(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.config(bg=COLORS["bg_sidebar_active"], fg=COLORS["text_light"],
                           font=FONTS["sidebar_bold"])
            else:
                btn.config(bg=COLORS["bg_sidebar"], fg=COLORS["text_secondary"],
                           font=FONTS["sidebar"])

    # ---------------------------------------------------------------
    def show_view(self, key):
        self.current_view = key
        self._update_nav_selection(key)

        for widget in self.content.winfo_children():
            widget.destroy()

        if key == "dashboard":
            view = DashboardView(self.content, self)
        elif key == "income":
            view = IncomeExpenseView(self.content, self, type_="income")
        elif key == "expense":
            view = IncomeExpenseView(self.content, self, type_="expense")
        elif key == "budget":
            view = BudgetView(self.content, self)
        elif key == "report":
            view = ReportView(self.content, self)
        else:
            view = DashboardView(self.content, self)

        view.pack(fill="both", expand=True)
        self.views[key] = view

    def refresh_all(self):
        """Dipanggil setelah ada perubahan data agar view yang sedang aktif diperbarui."""
        self.show_view(self.current_view)
