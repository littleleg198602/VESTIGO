from __future__ import annotations

from typing import Any

HEADER_TRANSLATIONS = {
    "Teilenummer der Leitung": ("Číslo dílu drátu", "Wire part number"),
    "Leitungsnummer": ("Číslo drátu", "Wire number"),
    "IST-Farbe": ("Skutečná barva (IST)", "Actual color (IST)"),
    "SOLL-Farbe": ("Požadovaná barva (SOLL)", "Required color (SOLL)"),
    "Farbe Ist": ("Skutečná barva (IST)", "Actual color (IST)"),
    "Farbe Soll": ("Požadovaná barva (SOLL)", "Required color (SOLL)"),
    "Potential": ("Potenciál", "Potential"),
    "Grundpotential": ("Základní potenciál", "Base potential"),
    "Meldung": ("Zpráva", "Message"),
    "Startpunkt": ("Start", "Start point"),
    "Endpunkt": ("Konec", "End point"),
    "Leitungen": ("Dráty", "Wires"),
    "Leitungslänge": ("Délka vedení", "Wire length"),
    "Ergebnis Hinweis": ("Výsledek", "Result note"),
    "Signalname": ("Název signálu", "Signal name"),
    "Signal": ("Signál", "Signal"),
    "Sonderleitung": ("Speciální drát", "Special cable"),
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


MESSAGE_VALUE_REPLACEMENTS = {
    "der winkel muss größer als 30° sein.": (
        "Úhel musí být větší než 30°.",
        "The angle must be greater than 30°.",
    ),
    "verknüpfte accessories": (
        "Propojené příslušenství",
        "Linked accessories",
    ),
    "bündellänge am splice darf nicht länger als 100 mm sein": (
        "Délka svazku na spoji nesmí být delší než 100 mm",
        "Bundle length at splice must not exceed 100 mm",
    ),
}


def translate_value(header: str, value: str, lang: str) -> str:
    """Translate known German free-text fragments in values for CZ/EN outputs."""
    if not value:
        return value

    normalized_header = clean_value(header).lower()
    if normalized_header not in {"meldung", "zpráva", "message"}:
        return value

    translated = value
    lowered = translated.lower()
    for source, (cz_target, en_target) in MESSAGE_VALUE_REPLACEMENTS.items():
        if source in lowered:
            target = cz_target if lang == "cz" else en_target
            start = lowered.index(source)
            end = start + len(source)
            translated = translated[:start] + target + translated[end:]
            lowered = translated.lower()
    return translated
