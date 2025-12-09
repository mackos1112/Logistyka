"""
CPM (Critical Path Method) - prosty, rozszerzalny moduł w Pythonie
Autor: ChatGPT
Język: polski (komentarze)

Funkcje:
- Reprezentacja czynności (Activity) oraz zdarzeń/węzłów (Event)
- Przechowywanie danych w kontenerach (listy, dict)
- Równoległy import danych (ręczne wprowadzanie / CSV)
- Obliczanie terminów w przodu (ES, EF) i w tył (LS, LF)
- Obliczanie zapasów (total float, free float)
- Wykrywanie—krytyczna ścieżka (lista czynności i zdarzeń)
- Prosty CLI-demonstrator

Plany rozbudowy:
- UI (tkinter / Flask / FastAPI / Streamlit)
- Wykres Gantta (matplotlib / plotly)
- Zapis i odczyt z plików (CSV/JSON/DB)

Uwaga: kod jest modularny i gotowy do rozszerzeń.
"""

import tkinter as tk
from cpm_gui import CPMGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = CPMGUI(root)
    root.mainloop()

