from __future__ import annotations

from dataclasses import dataclass


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
    object_type_cz: str = "Drát"
    object_type_en: str = "Wire"
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
    object_type_cz: str = "Drát",
    object_type_en: str = "Wire",
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
        object_type_cz=object_type_cz,
        object_type_en=object_type_en,
        handler=handler,
    )


RC_DEFINITIONS: dict[int, RCDefinition] = {
    1: _rc(1, "LIN drát - povolené číslo dílu", "LIN wire - approved part number", "Ověřuje, zda vodiče použité pro sběrnici LIN patří do povoleného rozsahu čísel dílů.", "This check verifies that the wire part number matches the approved LIN list.", ["Leitungsnummer", "Teilenummer der Leitung"], ["Teilenummer der Leitung", "Prüfung Parameter"], "Změnit číslo dílu drátu na povolený typ pro LIN.", "Change the wire part number to an approved LIN type.", object_type_cz="Drát", object_type_en="Wire", handler="rc1"),
    106: _rc(106, "Shoda barvy drátu a signálu", "Wire and signal color consistency", "Kontrola porovnává skutečnou a požadovanou barvu drátu pro daný signál.", "This check compares actual and required wire color for the given signal.", ["Signalname", "Signal"], ["IST-Farbe", "SOLL-Farbe", "Farben-Übereinstimmung"], "Ověřit a opravit shodu barvy drátu s potenciálovou listinou.", "Verify and correct the wire color against the potential list.", object_type_cz="Drát", object_type_en="Wire", handler="rc106"),
    110: _rc(110, "Kontrola délky speciálního vedení", "Special cable length consistency", "Maximální povolený rozdíl délek pro CAN: 50 mm\nMaximální povolený rozdíl délek pro FR: 10 mm\nMaximální povolený rozdíl délek pro ETH: 6 mm\nKontroluje, zda rozdíl délek mezi speciálními vlákny nepřesahuje maximální povolenou hodnotu.", "This check evaluates length differences between wires in a special cable.", ["Sonderleitung", "Leitungen"], ["Sonderleitung", "Teilenummer", "Leitungen", "Potentiale", "Leitungslänge", "Ermittelte Längendifferenz (DMU)"], "Zkontrolovat délku vedení a upravit trasu nebo definici.", "Check the wire length and adjust routing or definition.", object_type_cz="Speciální drát", object_type_en="Special cable", handler="rc110"),
    112: _rc(112, "Kontrola svazku", "Bundle consistency check", "Kontrola ověřuje konzistenci svazku drátů.", "This check verifies wire bundle consistency.", ["Leitungsnummer"], ["Meldung", "Leitungsnummer"], "Opravit záznam svazku podle pravidla RC.", "Correct the bundle record according to the RC rule.", object_type_cz="Splice", object_type_en="Splice"),
    115: _rc(115, "Kontrola ukončení drátu", "Wire end termination check", "Kontrola ověřuje správnost ukončení drátu.", "This check verifies correct wire end termination.", ["Leitungsnummer", "Endpunkt"], ["Startpunkt", "Endpunkt", "Meldung"], "Zkontrolovat ukončení drátu a opravit nesoulad.", "Verify wire termination and correct the mismatch.", object_type_cz="Konektor", object_type_en="Connector"),
    121: _rc(121, "Splice - shoda barev a potenciálu", "Splice - color and potential consistency", "Kontrola ověřuje konzistenci drátů ve splice podle VOBES-ID.", "This check verifies splice wire consistency by VOBES-ID.", ["Splice", "VOBES-ID"], ["VOBES-ID", "Leitungsnummer", "Farbe Ist", "Farbe Soll", "Potential"], "Sjednotit barvy a potenciály drátů uvnitř splice.", "Align wire colors and potentials within the splice.", object_type_cz="Splice", object_type_en="Splice", handler="rc121"),
    191: _rc(191, "Kontrola atributů vedení", "Wire attribute check", "Kontrola ověřuje povinné atributy vedení.", "This check verifies required wire attributes.", ["Leitungsnummer"], ["Meldung", "Leitungsnummer"], "Doplnit nebo opravit atributy vedení.", "Complete or correct wire attributes.", object_type_cz="Drát", object_type_en="Wire"),
    314: _rc(314, "Kontrola signálu", "Signal consistency check", "Kontrola ověřuje návaznost signálu na vedení.", "This check verifies signal mapping to wire.", ["Signalname"], ["Signal", "Meldung"], "Opravit mapování signálu na vedení.", "Correct signal-to-wire mapping.", object_type_cz="Signál", object_type_en="Signal"),
    325: _rc(325, "Kontrola zemnění", "Grounding consistency check", "Kontrola ověřuje konzistenci zemnění.", "This check verifies grounding consistency.", ["Potential"], ["Grundpotential", "Meldung"], "Opravit definici zemnění podle standardu.", "Correct grounding definition according to standard.", object_type_cz="Drát", object_type_en="Wire"),
    338: _rc(338, "Kontrola polohy komponentu", "Component position check", "Kontrola ověřuje, zda poloha komponentu v datovém modelu odpovídá požadované poloze (SOLL) z mateřského seznamu nebo KBL specifikace.", "This check verifies whether the component position in the data model matches the required (SOLL) position from the master list or KBL specification.", ["Bauteil", "VOBES-ID", "Verwendungsstelle"], ["SOLL-Position (Mutterliste)", "IST-Position (Y-Koordinate)", "Meldung"], "Zkontrolovat použitou komponentu/konektor, porovnat SOLL vs. IST pozici a upravit umístění nebo vazbu v datech.", "Check the used component/connector, compare SOLL vs IST position, and fix placement or mapping in data.", object_type_cz="Konektor", object_type_en="Connector"),
    350: _rc(350, "Kontrola komponenty", "Component consistency check", "Kontrola ověřuje konzistenci dat komponenty.", "This check verifies component data consistency.", ["Komponente"], ["Meldung", "Komponente"], "Opravit datový záznam komponenty.", "Correct the component data record.", object_type_cz="Komponenta", object_type_en="Component"),
    610: _rc(610, "Kontrola pojistky", "Fuse consistency check", "Kontrola ověřuje správnost dat pojistky.", "This check verifies fuse data correctness.", ["Sicherungsname", "Sicherungstyp"], ["Sicherungsname", "Sicherungstyp", "Meldung"], "Opravit datový záznam pojistky podle standardu.", "Correct the fuse data record according to the standard.", object_type_cz="Pojistka", object_type_en="Fuse"),
    907: _rc(907, "Kontrola větve svazku", "Harness branch check", "Kontrola ověřuje konzistenci větve svazku.", "This check verifies harness branch consistency.", ["Leitungspfad"], ["Leitungspfad", "Meldung"], "Opravit definici větve svazku.", "Correct the harness branch definition.", object_type_cz="Svazek", object_type_en="Harness"),
    1005: _rc(1005, "Kontrola pojistky", "Fuse consistency check", "Kontrola ověřuje konzistenci dat pojistky.", "This check verifies fuse data consistency.", ["Sicherungsname", "Sicherungstyp"], ["Sicherungsname", "Sicherungstyp", "Meldung"], "Opravit nastavení pojistky dle pravidla.", "Correct fuse setup according to rule.", object_type_cz="Pojistka", object_type_en="Fuse"),
    1007: _rc(1007, "Kontrola použití konektoru", "Connector usage point check", "Kontrola ověřuje, zda je u konektoru uvedena použitá pozice (Verwendungsstelle) a zda odpovídá údajům v mateřském seznamu.", "This check verifies that a connector usage point (Verwendungsstelle) is provided and matches the master-list data.", ["Bauteil", "VOBES-ID", "Verwendungsstelle"], ["Verwendungsstelle", "Meldung"], "Doplnit nebo opravit použitou pozici konektoru dle mateřského seznamu.", "Add or correct the connector usage point according to the master list.", object_type_cz="Konektor", object_type_en="Connector"),
    3001: _rc(3001, "Kontrola délky trasy vedení", "Wire route length check", "Kontrola vyhodnocuje délku trasy vedení vůči očekávaným hodnotám.", "This check evaluates wire route length against expected values.", ["Potential"], ["Potential", "Startpunkt", "Leitungsnummer", "Leitungslänge [mm]", "Endpunkt", "Gesamtlänge", "Ergebnis Hinweis"], "Prověřit trasu vedení a upravit délku nebo definici trasy.", "Review wire path and adjust length or route definition.", object_type_cz="Drát", object_type_en="Wire"),
    3002: _rc(3002, "Kontrola geometrie propojení", "Connection geometry check", "Kontrola porovnává délku vedení s vzdáleností koncových bodů.", "This check compares wire length and endpoint distance.", ["Startpunkt", "Endpunkt", "Potential"], ["Startpunkt", "Endpunkt", "Potential", "Σ Leitungslänge [mm]", "Abstand Endpunkte [mm]", "Ergebnis Hinweis", "Leitungspfad"], "Prověřit geometrii vedení a upravit trasu.", "Review connection geometry and adjust routing.", object_type_cz="Spoj", object_type_en="Connection"),
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
        ["Potential", "Meldung"],
        ["Meldung", "Potential"],
        "Zkontrolovat datový záznam podle pravidla RC.",
        "Check the data record according to the RC rule.",
        object_type_cz="Objekt",
        object_type_en="Object",
    )
