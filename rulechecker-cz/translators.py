from __future__ import annotations

from typing import Any

HEADER_TRANSLATIONS = {
    "Teilenummer der Leitung": ("Číslo dílu vodiče", "Wire part number"),
    "Leitungsnummer": ("Číslo vedení", "Wire number"),
    "IST-Farbe": ("Skutečná barva (IST)", "Actual color (IST)"),
    "SOLL-Farbe": ("Požadovaná barva (SOLL)", "Required color (SOLL)"),
    "Farbe Ist": ("Skutečná barva (IST)", "Actual color (IST)"),
    "Farbe Soll": ("Požadovaná barva (SOLL)", "Required color (SOLL)"),
    "Potential": ("Potenciál", "Potential"),
    "Grundpotential": ("Základní potenciál", "Base potential"),
    "Meldung": ("Zpráva", "Message"),
    "Startpunkt": ("Start", "Start point"),
    "Endpunkt": ("Konec", "End point"),
    "Leitungen": ("Vodiče", "Wires"),
    "Leitungslänge": ("Délka vedení", "Wire length"),
    "Ergebnis Hinweis": ("Výsledek", "Result note"),
    "Signalname": ("Název signálu", "Signal name"),
    "Signal": ("Signál", "Signal"),
    "Sonderleitung": ("Speciální vedení", "Special cable"),
    "Leitungslänge [mm]": ("Délka vedení [mm]", "Wire length [mm]"),
    "Σ Leitungslänge [mm]": ("Σ délka vedení [mm]", "Σ wire length [mm]"),
    "Abstand Endpunkte [mm]": ("Vzdálenost koncových bodů [mm]", "Distance between endpoints [mm]"),
    "Ermittelte Längendifferenz (DMU)": ("Zjištěný rozdíl délky (DMU)", "Detected length difference (DMU)"),
    "Prüfung Parameter": ("Parametr kontroly", "Check parameter"),
    "VOBES-ID": ("VOBES-ID", "VOBES-ID"),
    "Leitungspfad": ("Trasa vedení", "Wire path"),
}


def translate_header(header: str, lang: str) -> str:
    pair = HEADER_TRANSLATIONS.get(header)
    if not pair:
        return header
    return pair[0] if lang == "cz" else pair[1]


def clean_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()
