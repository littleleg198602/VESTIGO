from __future__ import annotations

from pathlib import Path

INPUT_DIR = Path(r"C:\Users\wzds96\Documents\Vestigo")
OUTPUT_DIR = INPUT_DIR

PROBLEM_STATUSES = {"Warnung", "Nicht in Ordnung", "Fehler", "Zu prüfen"}
IGNORE_STATUSES = {"In Ordnung", "Nicht bewertbar"}

OUTPUT_SHEET_CZ = "Prehled_CZ"
OUTPUT_SHEET_EN = "Overview_EN"
CRITICAL_SHEET_CZ = "Kriticke_CZ"
CRITICAL_SHEET_EN = "Critical_EN"
NON_CRITICAL_SHEET_CZ = "Nekriticke_CZ"
NON_CRITICAL_SHEET_EN = "NonCritical_EN"
LEGACY_INSPIRED_SHEET_EN = "LegacyInspired_EN"

OUTPUT_PATTERN_HINTS = [
    "__prehled_cz.xlsx",
    "__prehled_cz_",
    "__prehled_cz_en.xlsx",
    "__prehled_cz_en__",
    "__overview",
]

HEADER_STATUS_NAME = "Einschätzung"
HEADER_PARAM_NAME = "Prüfung Parameter"
