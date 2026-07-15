"""
main.py
Entry point aplikasi MoneyWise - Personal Finance Manager.
Jalankan dengan: python main.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.main_view import MainView


def main():
    app = MainView()
    app.mainloop()


if __name__ == "__main__":
    main()
