from __future__ import annotations

from typing import Any

import math
import re
import unicodedata

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
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        if value.is_integer():
            return str(int(value))
    text_value = str(value).strip()
    if text_value.lower() in {"nan", "none"}:
        return ""
    return text_value




def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "")
    return " ".join(normalized.split())


def _replace_fragment_case_insensitive(text: str, source: str, target: str) -> str:
    pattern = re.escape(_normalize_text(source)).replace(r"\ ", r"\s+")
    return re.sub(pattern, target, text, flags=re.IGNORECASE)

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
    "verpolung ist unbekannt.": (
        "Přepólování je neznámé.",
        "Reverse polarity is unknown.",
    ),
    "die leitungsfarbe entspricht nicht der vorgabe aus dem lastenheft": (
        "Barva vodiče neodpovídá požadavku ze specifikace.",
        "Wire color does not match the specification requirement.",
    ),
    "teilnehmer des lin-busses sind mit unterschiedlichen massebolzen verbunden.": (
        "Účastníci LIN sběrnice jsou připojeni na různé zemnící body.",
        "LIN bus participants are connected to different ground points.",
    ),
    "stecker hat keine masseleitung.": (
        "Konektor nemá zemnicí vedení.",
        "Connector has no ground wire.",
    ),
}


def translate_value(header: str, value: str, lang: str) -> str:
    """Translate known German free-text fragments in values for CZ/EN outputs."""
    if not value:
        return value

    normalized_header = clean_value(header).lower()
    if normalized_header not in {"meldung", "zpráva", "message"}:
        return value

    translated = _normalize_text(value)
    lowered = translated.lower()
    for source, (cz_target, en_target) in MESSAGE_VALUE_REPLACEMENTS.items():
        if _normalize_text(source) in lowered:
            target = cz_target if lang == "cz" else en_target
            translated = _replace_fragment_case_insensitive(translated, source, target)
            lowered = translated.lower()
    return translated


METADATA_TEXT_REPLACEMENTS = {
    "leitung: überprüfung der längendifferenz zwischen den sonderleitungscores": (
        "Vedení: kontrola rozdílu délky mezi jádry speciálního vedení",
        "Wire: check of length difference between special-cable cores",
    ),
    "leitung: ueberpruefung der laengendifferenz zwischen den sonderleitungscores": (
        "Vedení: kontrola rozdílu délky mezi jádry speciálního vedení",
        "Wire: check of length difference between special-cable cores",
    ),
    "splice: überprüfung der bündellänge am splice": (
        "Splice: kontrola délky svazku na spoji",
        "Splice: check of bundle length at splice",
    ),
    "splice: ueberpruefung der buendellaenge am splice": (
        "Splice: kontrola délky svazku na spoji",
        "Splice: check of bundle length at splice",
    ),
    "stecker: überprüfung der 3d-ausrichtung von (gedichteten) steckern": (
        "Konektor: kontrola 3D orientace (utěsněných) konektorů",
        "Connector: check of 3D orientation of (sealed) connectors",
    ),
    "prüft, ob die längendifferenz zwischen den sonderleitungscores": (
        "Kontrola ověřuje, zda rozdíl délky mezi jádry speciálního vedení",
        "Checks whether the length difference between special-cable cores",
    ),
    "prueft, ob die laengendifferenz zwischen den sonderleitungscores": (
        "Kontrola ověřuje, zda rozdíl délky mezi jádry speciálního vedení",
        "Checks whether the length difference between special-cable cores",
    ),
    "prüft, ob die maximale bündellänge am splice eingehalten wird.": (
        "Kontrola ověřuje, zda je dodržena maximální délka svazku na spoji.",
        "Checks whether the maximum bundle length at the splice is respected.",
    ),
    "prueft, ob die maximale buendellaenge am splice eingehalten wird.": (
        "Kontrola ověřuje, zda je dodržena maximální délka svazku na spoji.",
        "Checks whether the maximum bundle length at the splice is respected.",
    ),
    "prüft, ob die 3d-ausrichtung (gedichteter) stecker den grenzwert überschreitet.": (
        "Kontrola ověřuje, zda 3D orientace (utěsněných) konektorů překračuje mezní hodnotu.",
        "Checks whether the 3D orientation of (sealed) connectors exceeds the limit value.",
    ),
    "überprüfung der": ("Kontrola", "Check of"),
    "prüft, ob": ("Kontrola ověřuje, zda", "Checks whether"),
}


def translate_metadata_text(value: str, lang: str) -> str:
    """Translate common German Name/Beschreibung sheet metadata into CZ/EN."""
    text_value = clean_value(value)
    if not text_value:
        return text_value

    translated = _normalize_text(text_value)
    lowered = translated.lower()
    for source, (cz_target, en_target) in METADATA_TEXT_REPLACEMENTS.items():
        if _normalize_text(source) in lowered:
            target = cz_target if lang == "cz" else en_target
            translated = _replace_fragment_case_insensitive(translated, source, target)
            lowered = translated.lower()

    return translated
