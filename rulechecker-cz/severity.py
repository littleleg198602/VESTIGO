from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeverityLabels:
    cz: str
    en: str


STATE_TO_SEVERITY = {
    "Fehler": SeverityLabels("Kritické", "Critical"),
    "Nicht in Ordnung": SeverityLabels("Kritické", "Critical"),
    "Warnung": SeverityLabels("Nekritické", "Non-critical"),
    "Zu prüfen": SeverityLabels("Nekritické", "Non-critical"),
}


def map_status_to_severity(status: str) -> SeverityLabels | None:
    return STATE_TO_SEVERITY.get((status or "").strip())
