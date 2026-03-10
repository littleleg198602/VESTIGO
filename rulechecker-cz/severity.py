from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeverityLabels:
    cz: str
    en: str


STATE_TO_SEVERITY = {
    "fehler": SeverityLabels("Kritické", "Critical"),
    "nicht in ordnung": SeverityLabels("Kritické", "Critical"),
    "warnung": SeverityLabels("Nekritické", "Non-critical"),
    "zu prüfen": SeverityLabels("Nekritické", "Non-critical"),
    "zu pruefen": SeverityLabels("Nekritické", "Non-critical"),
    "error": SeverityLabels("Kritické", "Critical"),
    "not ok": SeverityLabels("Kritické", "Critical"),
    "warning": SeverityLabels("Nekritické", "Non-critical"),
    "to check": SeverityLabels("Nekritické", "Non-critical"),
}


def _normalize_status(status: str) -> str:
    return " ".join((status or "").strip().lower().split())


def map_status_to_severity(status: str) -> SeverityLabels | None:
    return STATE_TO_SEVERITY.get(_normalize_status(status))
