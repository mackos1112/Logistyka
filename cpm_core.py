from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import collections


def normalize(text: str) -> str:
    if text is None:
        return ""
    return (
        str(text)
        .replace("’", "'")
        .replace("‘", "'")
        .replace("`", "'")
        .replace("“", '"')
        .replace("”", '"')
        .strip()
    )


# -------------------------
#   ZDARZENIE (EVENT)
# -------------------------
@dataclass
class Event:
    """Zdarzenie CPM (węzeł sieci).

    Pola:
    - id: numeryczne ID zdarzenia (int)
    - name: opis tekstowy (np. 'Start', 'Koniec fundamentów')
    - ES: najwcześniejszy czas zajścia zdarzenia
    - LF: najpóźniejszy czas zajścia zdarzenia
    """
    id: int
    name: str = ""
    ES: float = 0.0
    LF: Optional[float] = None


# -------------------------
#   CZYNNOŚĆ (ACTIVITY)
# -------------------------
@dataclass
class Activity:
    """Czynność CPM (łuk między zdarzeniami).

    Pola:
    - id: numeryczne ID czynności (int)
    - name: opis tekstowy
    - duration: czas trwania
    - start_event: ID zdarzenia początkowego (int)
    - end_event: ID zdarzenia końcowego (int)

    Wyniki obliczeń:
    - ES, EF, LS, LF, total_float, free_float, is_critical
    """
    id: int
    name: str
    duration: float
    start_event: int
    end_event: int

    ES: Optional[float] = None
    EF: Optional[float] = None
    LS: Optional[float] = None
    LF: Optional[float] = None
    total_float: Optional[float] = None
    free_float: Optional[float] = None
    is_critical: bool = False

    def __post_init__(self):
        if self.duration < 0:
            raise ValueError("Czas trwania czynności nie może być ujemny.")


# -------------------------
#   SIEĆ CPM (AOA)
# -------------------------
class CPMNetwork:
    """Sieć CPM oparta o zdarzenia (AOA – Activity On Arrow).

    - events: dict[event_id] = Event
    - activities: dict[activity_id] = Activity
    - outgoing[event_id] = list[activity_id] - czynności wychodzące ze zdarzenia
    - incoming[event_id] = list[activity_id] - czynności wchodzące do zdarzenia
    """

    def __init__(self):
        self.events: Dict[int, Event] = {}
        self.activities: Dict[int, Activity] = {}
        self.outgoing: Dict[int, List[int]] = collections.defaultdict(list)
        self.incoming: Dict[int, List[int]] = collections.defaultdict(list)

    # -------------------------
    # ZDARZENIA
    # -------------------------
    def add_event(self, event_id: int, name: str = ""):
        """Dodaje zdarzenie o numerycznym ID i nazwie tekstowej."""
        if event_id in self.events:
            raise KeyError(f"Zdarzenie o ID {event_id} już istnieje.")
        self.events[event_id] = Event(id=event_id, name=name)

    def remove_event(self, event_id: int):
        if event_id not in self.events:
            raise KeyError("Brak zdarzenia o podanym ID.")
        # nie pozwalamy usunąć zdarzenia, jeśli są powiązane czynności
        if self.outgoing.get(event_id) or self.incoming.get(event_id):
            raise ValueError("Nie można usunąć zdarzenia powiązanego z czynnościami.")
        del self.events[event_id]

    # -------------------------
    # CZYNNOŚCI
    # -------------------------
    def add_activity(self, activity: Activity):
        """Dodaje czynność między istniejącymi zdarzeniami."""
        if activity.id in self.activities:
            raise KeyError(f"Czynność o ID {activity.id} już istnieje.")

        if activity.start_event not in self.events:
            raise KeyError(f"Brak zdarzenia początkowego: {activity.start_event}")
        if activity.end_event not in self.events:
            raise KeyError(f"Brak zdarzenia końcowego: {activity.end_event}")
        if activity.start_event == activity.end_event:
            raise ValueError("Zdarzenie początkowe i końcowe czynności nie mogą być takie same.")

        self.activities[activity.id] = activity
        self.outgoing[activity.start_event].append(activity.id)
        self.incoming[activity.end_event].append(activity.id)

    def remove_activity(self, activity_id: int):
        if activity_id not in self.activities:
            raise KeyError("Brak czynności o podanym ID.")
        act = self.activities[activity_id]
        if activity_id in self.outgoing.get(act.start_event, []):
            self.outgoing[act.start_event].remove(activity_id)
        if activity_id in self.incoming.get(act.end_event, []):
            self.incoming[act.end_event].remove(activity_id)
        del self.activities[activity_id]

    # -------------------------
    # Sortowanie topologiczne po ZDARZENIACH
    # -------------------------
    def _topological_order_events(self) -> List[int]:
        """Zwraca listę ID zdarzeń w porządku topologicznym."""
        # stopnie wejściowe zdarzeń
        in_deg = {eid: 0 for eid in self.events}
        for act in self.activities.values():
            in_deg[act.end_event] += 1

        queue = collections.deque([eid for eid, d in in_deg.items() if d == 0])
        order = []

        while queue:
            u = queue.popleft()
            order.append(u)
            for act_id in self.outgoing.get(u, []):
                v = self.activities[act_id].end_event
                in_deg[v] -= 1
                if in_deg[v] == 0:
                    queue.append(v)

        if len(order) != len(self.events):
            raise ValueError("Graf zdarzeń zawiera cykle lub jest niespójny.")
        return order

    # -------------------------
    # Obliczenia CPM
    # -------------------------
    def compute(self):
        if not self.events or not self.activities:
            return

        topo_events = self._topological_order_events()

        # Inicjalizacja ES zdarzeń
        for ev in self.events.values():
            ev.ES = 0.0

        # FORWARD PASS – wg zdarzeń
        for eid in topo_events:
            ev = self.events[eid]
            for act_id in self.outgoing.get(eid, []):
                act = self.activities[act_id]
                # ES czynności = ES zdarzenia początkowego
                act.ES = ev.ES
                act.EF = act.ES + act.duration
                # aktualizujemy ES zdarzenia końcowego
                end_ev = self.events[act.end_event]
                end_ev.ES = max(end_ev.ES, act.EF)

        # czas projektu = max ES zdarzeń końcowych
        project_duration = max(ev.ES for ev in self.events.values())

        # BACKWARD PASS
        # Inicjalizacja LF zdarzeń na czas projektu
        for ev in self.events.values():
            ev.LF = project_duration

        # Przechodzimy zdarzenia w odwrotnej kolejności topologicznej
        for eid in reversed(topo_events):
            ev = self.events[eid]

            # dla każdej czynności wychodzącej ze zdarzenia
            for act_id in self.outgoing.get(eid, []):
                act = self.activities[act_id]
                end_ev = self.events[act.end_event]

                # LF czynności = LF zdarzenia końcowego
                act.LF = end_ev.LF
                act.LS = act.LF - act.duration

            # teraz aktualizujemy LF zdarzenia na podstawie czynności wychodzących
            if self.outgoing.get(eid):
                ev.LF = min(self.activities[a].LS for a in self.outgoing[eid])

        # ZAPASY I ŚCIEŻKA KRYTYCZNA
        for act in self.activities.values():
            if act.LS is None or act.ES is None:
                act.total_float = None
                act.free_float = None
                act.is_critical = False
                continue

            act.total_float = round(act.LS - act.ES, 6)
            # free float = ES zdarzenia końcowego - EF czynności
            end_ev = self.events[act.end_event]
            act.free_float = round(end_ev.ES - act.EF, 6)
            act.is_critical = abs(act.total_float) < 1e-9

        self._last_project_duration = project_duration

    # -------------------------
    # Ścieżka krytyczna
    # -------------------------
    def critical_path(self) -> Tuple[List[int], float]:
        """Zwraca listę ID czynności na ścieżce krytycznej oraz czas projektu."""
        self.compute()
        # sortujemy czynności wg zdarzenia początkowego (dla czytelności)
        topo_events = self._topological_order_events()
        pos = {eid: i for i, eid in enumerate(topo_events)}

        critical_acts = [a for a in self.activities.values() if a.is_critical]
        critical_acts_sorted = sorted(critical_acts, key=lambda ac: pos[ac.start_event])

        cp_ids = [ac.id for ac in critical_acts_sorted]
        duration = getattr(self, "_last_project_duration", 0.0)
        return cp_ids, duration

    # -------------------------
    # Podsumowanie projektu
    # -------------------------
    def project_summary(self) -> Dict:
        self.compute()
        events_out = []
        for eid in sorted(self.events):
            ev = self.events[eid]
            events_out.append({
                "id": ev.id,
                "name": ev.name,
                "ES": ev.ES,
                "LF": ev.LF,
            })

        activities_out = []
        for aid in sorted(self.activities):
            a = self.activities[aid]
            activities_out.append({
                "id": a.id,
                "name": a.name,
                "duration": a.duration,
                "start_event": a.start_event,
                "end_event": a.end_event,
                "ES": a.ES,
                "EF": a.EF,
                "LS": a.LS,
                "LF": a.LF,
                "total_float": a.total_float,
                "free_float": a.free_float,
                "is_critical": a.is_critical,
            })

        cp, duration = self.critical_path()
        return {
            "duration": duration,
            "critical_path": cp,
            "events": events_out,
            "activities": activities_out,
        }
