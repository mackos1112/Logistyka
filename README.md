# 🧮 CPM – Critical Path Method (AOA)  
Aplikacja do analizy sieci projektu w metodzie **CPM – Activity on Arrow (AOA)**  
z graficznym interfejsem użytkownika (Tkinter) oraz wykresem Gantta (Matplotlib).

---

## 📌 Funkcje aplikacji

✔ Dodawanie **zdarzeń (eventów)**:
- ID numeryczne  
- Nazwa tekstowa  
- Wykorzystywane jako węzły sieci  

✔ Dodawanie **czynności (activities)**:
- ID numeryczne  
- Nazwa tekstowa  
- Czas trwania (float / int)  
- Zdarzenie początkowe  
- Zdarzenie końcowe  

✔ Automatyczne obliczenia:
- ES / EF (terminy najwcześniejsze)
- LS / LF (terminy najpóźniejsze)
- Zapasy czasu (Total Float, Free Float)
- Oznaczenie czynności **krytycznych**
- Wyznaczenie **ścieżki krytycznej**  

✔ Wizualizacja:
- Czytelny wykres **Gantta** z wyróżnieniem ścieżki krytycznej  
  - czerwone paski – czynności krytyczne  
  - niebieskie paski – pozostałe  

✔ Interfejs GUI (Tkinter):
- osobne panele do dodawania zdarzeń i czynności  
- okno wyników CPM  
- okno wykresu Gantta  
- możliwość czyszczenia projektu  

---

## 🖥️ Technologia

- **Python 3.10+**
- Tkinter (GUI)
- Matplotlib (Gantt chart)
- Standardowa biblioteka (dataclasses, collections)

---

