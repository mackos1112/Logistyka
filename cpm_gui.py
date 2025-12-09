import tkinter as tk
from tkinter import ttk, messagebox
from typing import List
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from cpm_core import CPMNetwork, Activity, Event  # upewnij się, że nazwa pliku to cpm_core.py


class CPMGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPM – sieć zdarzeń (AOA)")

        self.net = CPMNetwork()

        main = ttk.Notebook(root)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_events = ttk.Frame(main)
        self.tab_activities = ttk.Frame(main)

        main.add(self.tab_events, text="Zdarzenia")
        main.add(self.tab_activities, text="Czynności")

        self._build_events_tab()
        self._build_activities_tab()

        # Przyciski globalne
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Oblicz CPM", command=self.compute_cpm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Wykres Gantta", command=self.show_gantt).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Wyczyść projekt", command=self.clear_all).pack(side=tk.LEFT, padx=5)

    # ---------------- Events tab ----------------
    def _build_events_tab(self):
        frm = self.tab_events

        ttk.Label(frm, text="ID zdarzenia (liczba):").grid(row=0, column=0, sticky="w")
        self.entry_event_id = ttk.Entry(frm, width=10)
        self.entry_event_id.grid(row=0, column=1, sticky="w")

        ttk.Label(frm, text="Nazwa zdarzenia:").grid(row=1, column=0, sticky="w")
        self.entry_event_name = ttk.Entry(frm, width=30)
        self.entry_event_name.grid(row=1, column=1, sticky="w")

        ttk.Button(frm, text="Dodaj zdarzenie", command=self.add_event).grid(row=2, column=0, columnspan=2, pady=5)

        ttk.Label(frm, text="Zdarzenia:").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.events_list = tk.Listbox(frm, width=50, height=10)
        self.events_list.grid(row=4, column=0, columnspan=2, sticky="w")

    # ---------------- Activities tab ----------------
    def _build_activities_tab(self):
        frm = self.tab_activities

        ttk.Label(frm, text="ID czynności (liczba):").grid(row=0, column=0, sticky="w")
        self.entry_act_id = ttk.Entry(frm, width=10)
        self.entry_act_id.grid(row=0, column=1, sticky="w")

        ttk.Label(frm, text="Nazwa czynności:").grid(row=1, column=0, sticky="w")
        self.entry_act_name = ttk.Entry(frm, width=30)
        self.entry_act_name.grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="Czas trwania:").grid(row=2, column=0, sticky="w")
        self.entry_act_dur = ttk.Entry(frm, width=10)
        self.entry_act_dur.grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Zdarzenie początkowe (ID):").grid(row=3, column=0, sticky="w")
        self.combo_start_event = ttk.Combobox(frm, state="readonly", width=10, values=[])
        self.combo_start_event.grid(row=3, column=1, sticky="w")

        ttk.Label(frm, text="Zdarzenie końcowe (ID):").grid(row=4, column=0, sticky="w")
        self.combo_end_event = ttk.Combobox(frm, state="readonly", width=10, values=[])
        self.combo_end_event.grid(row=4, column=1, sticky="w")

        ttk.Button(frm, text="Dodaj czynność", command=self.add_activity).grid(row=5, column=0, columnspan=2, pady=5)

        ttk.Label(frm, text="Czynności:").grid(row=6, column=0, sticky="w", pady=(10, 0))
        self.activities_list = tk.Listbox(frm, width=70, height=10)
        self.activities_list.grid(row=7, column=0, columnspan=2, sticky="w")

    # ------------- Actions: events -------------
    def add_event(self):
        eid_raw = self.entry_event_id.get().strip()
        name = self.entry_event_name.get().strip()

        if not eid_raw.isdigit():
            messagebox.showerror("Błąd", "ID zdarzenia musi być liczbą całkowitą.")
            return
        eid = int(eid_raw)

        try:
            self.net.add_event(eid, name)
        except Exception as e:
            messagebox.showerror("Błąd", str(e))
            return

        self.events_list.insert(tk.END, f"{eid}: {name}")
        self.entry_event_id.delete(0, tk.END)
        self.entry_event_name.delete(0, tk.END)

        self._refresh_event_comboboxes()

    def _refresh_event_comboboxes(self):
        ids = sorted(self.net.events.keys())
        values = [str(eid) for eid in ids]
        self.combo_start_event["values"] = values
        self.combo_end_event["values"] = values

    # ------------- Actions: activities -------------
    def add_activity(self):
        aid_raw = self.entry_act_id.get().strip()
        name = self.entry_act_name.get().strip()
        dur_raw = self.entry_act_dur.get().strip()
        start_raw = self.combo_start_event.get().strip()
        end_raw = self.combo_end_event.get().strip()

        if not aid_raw.isdigit():
            messagebox.showerror("Błąd", "ID czynności musi być liczbą całkowitą.")
            return
        aid = int(aid_raw)

        if not dur_raw:
            messagebox.showerror("Błąd", "Podaj czas trwania.")
            return
        try:
            dur = float(dur_raw)
        except ValueError:
            messagebox.showerror("Błąd", "Czas trwania musi być liczbą.")
            return

        if not start_raw or not end_raw:
            messagebox.showerror("Błąd", "Wybierz zdarzenie początkowe i końcowe.")
            return

        if not start_raw.isdigit() or not end_raw.isdigit():
            messagebox.showerror("Błąd", "ID zdarzeń musi być liczbą.")
            return

        start_id = int(start_raw)
        end_id = int(end_raw)

        try:
            act = Activity(id=aid, name=name, duration=dur,
                           start_event=start_id, end_event=end_id)
            self.net.add_activity(act)
        except Exception as e:
            messagebox.showerror("Błąd", str(e))
            return

        self.activities_list.insert(
            tk.END,
            f"{aid}: {name}, dur={dur}, {start_id} -> {end_id}"
        )

        self.entry_act_id.delete(0, tk.END)
        self.entry_act_name.delete(0, tk.END)
        self.entry_act_dur.delete(0, tk.END)
        self.combo_start_event.set("")
        self.combo_end_event.set("")

    # ------------- Actions: compute -------------
    def compute_cpm(self):
        try:
            summary = self.net.project_summary()
        except Exception as e:
            messagebox.showerror("Błąd CPM", str(e))
            return

        win = tk.Toplevel(self.root)
        win.title("Wyniki CPM")

        text = tk.Text(win, width=110, height=35)
        text.pack(padx=10, pady=10)

        text.insert(tk.END, f"Czas trwania projektu: {summary['duration']}\n")
        text.insert(tk.END, f"Ścieżka krytyczna (ID czynności): "
                            f"{' -> '.join(str(i) for i in summary['critical_path'])}\n\n")

        text.insert(tk.END, "ZDARZENIA:\n")
        for ev in summary["events"]:
            line = (f"Event {ev['id']} ({ev['name']}): "
                    f"ES={ev['ES']}, LF={ev['LF']}\n")
            text.insert(tk.END, line)
        text.insert(tk.END, "\nCZYNNOSCI:\n")
        for a in summary["activities"]:
            line = (f"Act {a['id']} ({a['name']}): "
                    f"dur={a['duration']}, "
                    f"{a['start_event']} -> {a['end_event']}, "
                    f"ES={a['ES']}, EF={a['EF']}, "
                    f"LS={a['LS']}, LF={a['LF']}, "
                    f"TF={a['total_float']}, FF={a['free_float']}, "
                    f"critical={a['is_critical']}\n")
            text.insert(tk.END, line)

    # ------------- Actions: clear -------------
    def clear_all(self):
        self.net = CPMNetwork()
        self.events_list.delete(0, tk.END)
        self.activities_list.delete(0, tk.END)
        self._refresh_event_comboboxes()
        messagebox.showinfo("Wyczyszczono", "Projekt został wyczyszczony.")

    def show_gantt(self):
        try:
            summary = self.net.project_summary()
        except Exception as e:
            messagebox.showerror("Błąd CPM", str(e))
            return

        acts = summary["activities"]

        if not acts:
            messagebox.showinfo("Brak danych", "Najpierw dodaj czynności.")
            return

        gantt_win = tk.Toplevel(self.root)
        gantt_win.title("Wykres Gantta")

        fig, ax = plt.subplots(figsize=(10, 6))

        y_labels = []
        y_positions = []

        for i, act in enumerate(acts):
            y_labels.append(f"{act['id']}: {act['name']}")
            y_positions.append(i)

            start = act["ES"]
            duration = act["duration"]

            color = "red" if act["is_critical"] else "skyblue"

            ax.barh(i, duration, left=start, color=color, edgecolor="black")
            ax.text(start + duration + 0.1, i, f"EF={act['EF']}", va='center')

        ax.set_yticks(y_positions)
        ax.set_yticklabels(y_labels)
        ax.set_xlabel("Czas")
        ax.set_title("Wykres Gantta – CPM (AOA)")

        ax.invert_yaxis()  # najwcześniejsze na górze
        ax.grid(True, axis='x', linestyle='--', alpha=0.6)

        canvas = FigureCanvasTkAgg(fig, master=gantt_win)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = CPMGUI(root)
    root.mainloop()
