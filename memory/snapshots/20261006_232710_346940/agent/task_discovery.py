"""Generic domain-agnostic discovery before implementing an unfamiliar task."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Discovery:
    goal: str
    unknowns: tuple[str, ...]
    research_questions: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]

def discover(goal: str) -> Discovery:
    clean = goal.strip()
    if not clean: raise ValueError("Zadanie musi mieć cel.")
    return Discovery(
        clean,
        ("wymagania", "ograniczenia", "źródła prawdy", "ryzyko", "kryteria sukcesu"),
        (f"Jakie są oficjalne źródła i standardy dla: {clean}?", f"Jakie rozwiązania są bezpłatne i dostępne lokalnie?", f"Jak zweryfikować rezultat zadania: {clean}?"),
        ("Każdy fakt ma źródło albo oznaczenie niepewności.", "Rezultat przechodzi test praktyczny.", "Ryzykowne działania są zatrzymane przed wykonaniem.")
    )
