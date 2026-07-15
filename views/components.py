"""
views/components.py
Kumpulan widget custom yang dapat dipakai ulang di berbagai View
agar tampilan konsisten dan modern.
"""

import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, CURRENCY_SYMBOL


def format_currency(amount):
    """Format angka menjadi format Rupiah, misal 1500000 -> Rp 1.500.000"""
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        amount = 0.0
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    formatted = f"{amount:,.0f}".replace(",", ".")
    return f"{sign}{CURRENCY_SYMBOL} {formatted}"


class Card(tk.Frame):
    """Kartu putih dengan sudut 'halus' (simulasi shadow) untuk membungkus konten."""

    def __init__(self, parent, bg=COLORS["bg_card"], padding=16, **kwargs):
        outer = kwargs.pop("outer_bg", COLORS["bg_main"])
        super().__init__(parent, bg=outer)
        self.container = tk.Frame(self, bg=bg, highlightbackground=COLORS["border"],
                                   highlightthickness=1, **kwargs)
        self.container.pack(fill="both", expand=True, padx=0, pady=0)
        self.inner = tk.Frame(self.container, bg=bg)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)


class StatCard(tk.Frame):
    """Kartu statistik ringkas: judul, nilai besar, dan indikator warna."""

    def __init__(self, parent, title, value, color, icon="●"):
        super().__init__(parent, bg=COLORS["bg_card"], highlightbackground=COLORS["border"],
                          highlightthickness=1)
        inner = tk.Frame(self, bg=COLORS["bg_card"])
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        top = tk.Frame(inner, bg=COLORS["bg_card"])
        top.pack(fill="x")
        tk.Label(top, text=icon, bg=COLORS["bg_card"], fg=color,
                  font=("Segoe UI", 14)).pack(side="left")
        tk.Label(top, text=title, bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                  font=FONTS["body"]).pack(side="left", padx=(8, 0))

        self.value_label = tk.Label(inner, text=value, bg=COLORS["bg_card"],
                                     fg=COLORS["text_primary"], font=FONTS["card_value"])
        self.value_label.pack(anchor="w", pady=(10, 0))

    def set_value(self, value):
        self.value_label.config(text=value)


class RoundedButton(tk.Button):
    """Tombol dengan gaya flat modern dan efek hover."""

    def __init__(self, parent, text, command=None, bg=COLORS["accent"],
                 fg=COLORS["text_light"], hover_bg=None, font=None, **kwargs):
        self.default_bg = bg
        self.hover_bg = hover_bg or COLORS["accent_dark"]
        super().__init__(
            parent, text=text, command=command, bg=bg, fg=fg,
            font=font or FONTS["body_bold"], relief="flat", bd=0,
            activebackground=self.hover_bg, activeforeground=fg,
            cursor="hand2", padx=16, pady=8, **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.default_bg))


class GhostButton(tk.Button):
    """Tombol outline/transparan untuk aksi sekunder."""

    def __init__(self, parent, text, command=None, fg=COLORS["accent"], **kwargs):
        super().__init__(
            parent, text=text, command=command, bg=COLORS["bg_card"], fg=fg,
            font=FONTS["body_bold"], relief="flat", bd=1,
            highlightbackground=fg, highlightthickness=1,
            activebackground=COLORS["bg_card_alt"], cursor="hand2",
            padx=14, pady=7, **kwargs
        )


class ScrollableFrame(tk.Frame):
    """Frame dengan scrollbar vertikal, dipakai untuk daftar panjang."""

    def __init__(self, parent, bg=COLORS["bg_main"]):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class PlaceholderEntry(tk.Entry):
    """Entry dengan placeholder text bawaan."""

    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = COLORS["text_secondary"]
        self.default_fg = kwargs.get("fg", COLORS["text_primary"])
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, event=None):
        if self.get() == self.placeholder:
            self.delete(0, "end")
            self.config(fg=self.default_fg)

    def _add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

    def get_value(self):
        val = self.get()
        return "" if val == self.placeholder else val


def make_progress_bar(parent, percent, color, bg=COLORS["bg_card_alt"], width=200, height=10):
    """Membuat progress bar sederhana menggunakan Canvas (tanpa dependensi luar)."""
    canvas = tk.Canvas(parent, width=width, height=height, bg=bg,
                        highlightthickness=0)
    percent = max(0, min(percent, 100))
    fill_width = int((percent / 100) * width)
    canvas.create_rectangle(0, 0, width, height, fill=bg, outline="")
    if fill_width > 0:
        canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")
    return canvas


class Badge(tk.Label):
    """Label kecil bergaya badge/pill, misal untuk kategori."""

    def __init__(self, parent, text, bg, fg):
        super().__init__(parent, text=f"  {text}  ", bg=bg, fg=fg,
                          font=FONTS["small"], padx=2, pady=2)
