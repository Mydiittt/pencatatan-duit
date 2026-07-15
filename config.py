"""
config.py
Konfigurasi global aplikasi: warna tema, font, konstanta, dan path database.
"""

import sys
import os

# Tentukan BASE_DIR agar database disimpan di folder yang sama dengan file executable (.exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "money_manager.db")

APP_NAME = "MoneyWise"
APP_VERSION = "1.0.0"

# ----------------------------
# PALET WARNA (Tema modern - dark sidebar + light content)
# ----------------------------
COLORS = {
    "bg_main": "#F4F6FA",          # background utama (terang)
    "bg_sidebar": "#1E2337",       # sidebar gelap
    "bg_sidebar_hover": "#2A2F47",
    "bg_sidebar_active": "#4C6FFF",
    "bg_card": "#FFFFFF",
    "bg_card_alt": "#F0F2F8",
    "text_primary": "#1E2337",
    "text_secondary": "#8A8FA3",
    "text_light": "#FFFFFF",
    "accent": "#4C6FFF",
    "accent_dark": "#3955D8",
    "income": "#22C55E",
    "income_bg": "#E8FBF0",
    "expense": "#EF4444",
    "expense_bg": "#FDECEC",
    "warning": "#F59E0B",
    "warning_bg": "#FFF6E5",
    "border": "#E5E8F0",
    "shadow": "#D8DCE8",
    "chart_colors": ["#4C6FFF", "#22C55E", "#F59E0B", "#EF4444", "#A855F7",
                      "#06B6D4", "#EC4899", "#84CC16", "#F97316", "#6366F1"],
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 13, "bold"),
    "heading": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "card_value": ("Segoe UI", 22, "bold"),
    "sidebar": ("Segoe UI", 11),
    "sidebar_bold": ("Segoe UI", 11, "bold"),
}

# Kategori default
DEFAULT_INCOME_CATEGORIES = [
    "Gaji", "Bonus", "Hadiah", "Investasi", "Bisnis", "Lainnya"
]

DEFAULT_EXPENSE_CATEGORIES = [
    "Makanan & Minuman", "Transportasi", "Belanja", "Tagihan",
    "Hiburan", "Kesehatan", "Pendidikan", "Rumah Tangga", "Lainnya"
]

CURRENCY_SYMBOL = "Rp"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 720
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 640
