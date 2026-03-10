from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class RCDefinition:
    rc: int
    title_cz: str
    title_en: str
    explanation_cz: str
    explanation_en: str
    affected_columns: list[str]
    issue_columns: list[str]
    recommendation_cz: str
    recommendation_en: str
    handler: str = "default"


def _rc(
    rc: int,
    title_cz: str,
    title_en: str,
    explanation_cz: str,
    explanation_en: str,
    affected_columns: list[str],
    issue_columns: list[str],
    recommendation_cz: str,
    recommendation_en: str,
    handler: str = "default",
) -> RCDefinition:
    return RCDefinition(
        rc=rc,
        title_cz=title_cz,
        title_en=title_en,
        explanation_cz=explanation_cz,
        explanation_en=explanation_en,
        affected_columns=affected_columns,
        issue_columns=issue_columns,
        recommendation_cz=recommendation_cz,
        recommendation_en=recommendation_en,
        handler=handler,
    )


RC_DEFINITIONS: dict[int, RCDefinition] = {
    1: _rc(
        1,
        "LIN vodič - povolené číslo dílu",
        "LIN wire - approved part number",
        "Kontrola ověřuje, že číslo dílu vodiče odpovídá povolenému seznamu pro LIN.",
        "This check verifies that the wire part number matches the approved LIN list.",
        ["Leitungsnummer", "Teilenummer der Leitung"],
        ["Teilenummer der Leitung", "Prüfung Parameter"],
        "Změnit číslo dílu vodiče na povolený typ pro LIN.",
        "Change the wire part number to an approved LIN type.",
        handler="rc1",
    ),
    106: _rc(
        106,
        "Shoda barvy vodiče a signálu",
        "Wire and signal color consistency",
        "Kontrola porovnává skutečnou a požadovanou barvu vodiče pro daný signál.",
        "This check compares actual and required wire color for the given signal.",
        ["Leitungsnummer", "Signalname", "Signal"],
        ["IST-Farbe", "SOLL-Farbe", "Farben-Übereinstimmung"],
        "Ověřit a opravit shodu barvy vodiče s potenciálovou listinou.",
        "Verify and correct the wire color against the potential list.",
        handler="rc106",
    ),
    110: _rc(
        110,
        "Kontrola délky speciálního vedení",
        "Special cable length consistency",
        "Kontrola vyhodnocuje rozdíl délek mezi vodiči ve speciálním vedení.",
        "This check evaluates length differences between wires in a special cable.",
        ["Sonderleitung", "Leitungen"],
        [
            "Sonderleitung",
            "Teilenummer",
            "Leitungen",
            "Potentiale",
            "Leitungslänge",
            "Ermittelte Längendifferenz (DMU)",
        ],
        "Zkontrolovat délku vedení a upravit trasu nebo definici.",
        "Check the wire length and adjust routing or definition.",
        handler="rc110",
    ),
    112: _rc(112, "Kontrola svazku", "Bundle consistency check", "Kontrola ověřuje konzistenci svazku vodičů.", "This check verifies wire bundle consistency.", ["Leitungsnummer"], ["Meldung", "Leitungsnummer"], "Opravit záznam svazku podle pravidla RC.", "Correct the bundle record according to the RC rule."),
    115: _rc(115, "Kontrola ukončení vodiče", "Wire end termination check", "Kontrola ověřuje správnost ukončení vodiče.", "This check verifies correct wire end termination.", ["Leitungsnummer", "Endpunkt"], ["Startpunkt", "Endpunkt", "Meldung"], "Zkontrolovat ukončení vodiče a opravit nesoulad.", "Verify wire termination and correct the mismatch."),
    121: _rc(
        121,
        "Splice - shoda barev a potenciálu",
        "Splice - color and potential consistency",
        "Kontrola ověřuje konzistenci vodičů ve splice podle VOBES-ID.",
        "This check verifies splice wire consistency by VOBES-ID.",
        ["Splice", "VOBES-ID"],
        ["VOBES-ID", "Leitungsnummer", "Farbe Ist", "Farbe Soll", "Potential"],
        "Sjednotit barvy a potenciály vodičů uvnitř splice.",
        "Align wire colors and potentials within the splice.",
        handler="rc121",
    ),
    191: _rc(191, "Kontrola atributů vedení", "Wire attribute check", "Kontrola ověřuje povinné atributy vedení.", "This check verifies required wire attributes.", ["Leitungsnummer"], ["Meldung", "Leitungsnummer"], "Doplnit nebo opravit atributy vedení.", "Complete or correct wire attributes."),
    314: _rc(314, "Kontrola signálu", "Signal consistency check", "Kontrola ověřuje návaznost signálu na vedení.", "This check verifies signal mapping to wire.", ["Signalname", "Leitungsnummer"], ["Signal", "Meldung"], "Opravit mapování signálu na vedení.", "Correct signal-to-wire mapping."),
    325: _rc(325, "Kontrola zemnění", "Grounding consistency check", "Kontrola ověřuje konzistenci zemnění.", "This check verifies grounding consistency.", ["Potential", "Leitungsnummer"], ["Grundpotential", "Meldung"], "Opravit definici zemnění podle standardu.", "Correct grounding definition according to standard."),
    338: _rc(338, "Kontrola napájení", "Power supply consistency check", "Kontrola ověřuje konzistenci napájecí větve.", "This check verifies power branch consistency.", ["Potential", "Leitungsnummer"], ["Meldung", "Potential"], "Opravit datový záznam napájení.", "Correct the power supply data record."),
    350: _rc(350, "Kontrola komponenty", "Component consistency check", "Kontrola ověřuje konzistenci dat komponenty.", "This check verifies component data consistency.", ["Komponente", "Leitungsnummer"], ["Meldung", "Komponente"], "Opravit datový záznam komponenty.", "Correct the component data record."),
    610: _rc(610, "Kontrola pojistky", "Fuse consistency check", "Kontrola ověřuje správnost dat pojistky.", "This check verifies fuse data correctness.", ["Sicherungsname", "Sicherungstyp"], ["Sicherungsname", "Sicherungstyp", "Meldung"], "Opravit datový záznam pojistky podle standardu.", "Correct the fuse data record according to the standard."),
    907: _rc(907, "Kontrola větve svazku", "Harness branch check", "Kontrola ověřuje konzistenci větve svazku.", "This check verifies harness branch consistency.", ["Leitungspfad", "Leitungsnummer"], ["Leitungspfad", "Meldung"], "Opravit definici větve svazku.", "Correct the harness branch definition."),
    1005: _rc(1005, "Kontrola varianty", "Variant consistency check", "Kontrola ověřuje konzistenci variantních dat.", "This check verifies variant data consistency.", ["Variant", "Leitungsnummer"], ["Variant", "Meldung"], "Opravit variantní nastavení dle pravidla.", "Correct variant setup according to rule."),
    1007: _rc(1007, "Kontrola propojení", "Connection consistency check", "Kontrola ověřuje konzistenci propojení.", "This check verifies connection consistency.", ["Startpunkt", "Endpunkt"], ["Startpunkt", "Endpunkt", "Meldung"], "Opravit propojení mezi body podle pravidla.", "Correct the connection between points according to rule."),
    3001: _rc(
        3001,
        "Kontrola délky trasy vedení",
        "Wire route length check",
        "Kontrola vyhodnocuje délku trasy vedení vůči očekávaným hodnotám.",
        "This check evaluates wire route length against expected values.",
        ["Leitungsnummer", "Potential"],
        ["Potential", "Startpunkt", "Leitungsnummer", "Leitungslänge [mm]", "Endpunkt", "Gesamtlänge", "Ergebnis Hinweis"],
        "Prověřit trasu vedení a upravit délku nebo definici trasy.",
        "Review wire path and adjust length or route definition.",
    ),
    3002: _rc(
        3002,
        "Kontrola geometrie propojení",
        "Connection geometry check",
        "Kontrola porovnává délku vedení s vzdáleností koncových bodů.",
        "This check compares wire length and endpoint distance.",
        ["Startpunkt", "Endpunkt", "Potential"],
        ["Startpunkt", "Endpunkt", "Potential", "Σ Leitungslänge [mm]", "Abstand Endpunkte [mm]", "Ergebnis Hinweis", "Leitungspfad"],
        "Prověřit geometrii vedení a upravit trasu.",
        "Review connection geometry and adjust routing.",
    ),
}


def get_rc_definition(rc: int) -> RCDefinition:
    if rc in RC_DEFINITIONS:
        return RC_DEFINITIONS[rc]
    return _rc(
        rc,
        f"RC {rc} – Kontrola",
        f"RC {rc} - Check",
        "Kontrola ověřuje správnost dat podle definovaného pravidla.",
        "This check verifies data correctness according to the defined rule.",
        ["Leitungsnummer", "Potential", "Meldung"],
        ["Meldung", "Leitungsnummer", "Potential"],
        "Zkontrolovat datový záznam podle pravidla RC.",
        "Check the data record according to the RC rule.",
    )
