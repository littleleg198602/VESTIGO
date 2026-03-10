# rulechecker-cz

Python projekt pro zpracování Excel reportů z RuleChecker / Capital Harness Analyzer.
Nástroj pro každý vstupní report vytvoří nový výstupní `.xlsx` s přehledem problémů ve dvou jazycích (čeština + angličtina), včetně rozdělení na kritické a nekritické položky.

## Co projekt dělá

- Prochází všechny `.xlsx` soubory ve vstupním adresáři.
- Přeskakuje již vygenerované výstupy (`__prehled_CZ...`, `__prehled_CZ_EN...`, `__overview...`).
- Automaticky hledá řádek hlavičky i v listech, kde tabulka nezačíná na prvním řádku (typické pro exporty s metadaty nahoře).
- V listu RC zpracovává jen řádky se stavem:
  - `Warnung`
  - `Nicht in Ordnung`
  - `Fehler`
  - `Zu prüfen`
- Ignoruje:
  - `In Ordnung`
  - `Nicht bewertbar`
- Vytváří vždy 1 výstupní soubor pro 1 vstupní soubor ve formátu:
  - `<vstup>__prehled_CZ_EN__YYYYMMDD_HHMMSS.xlsx`
  - při kolizi názvu přidá `__01`, `__02`, ...
- Výstup obsahuje listy:
  - `Prehled_CZ`
  - `Overview_EN`
  - `Kriticke_CZ`
  - `Critical_EN`
  - `Nekriticke_CZ`
  - `NonCritical_EN`

## Instalace

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Spuštění

```bash
python main.py
```

Volitelně vlastní cesty:

```bash
python main.py --input-dir "C:/Users/wzds96/Documents/Vestigo" --output-dir "C:/Users/wzds96/Documents/Vestigo"
```

## Změna vstupního adresáře

Výchozí hodnoty jsou v `config.py` (`INPUT_DIR`, `OUTPUT_DIR`).
Můžete je změnit přímo v souboru nebo předat přes CLI argumenty.

## Mapování RC pravidel

- RC definice jsou centralizované v `rc_maps.py`.
- Každé RC má:
  - český a anglický název
  - české a anglické vysvětlení
  - mapu relevantních sloupců pro objekt a detail chyby
  - české a anglické doporučení
- Známé RC implementované v mapě:
  - 1, 106, 110, 112, 115, 121, 191, 314, 325, 338, 350, 610, 907, 1005, 1007, 3001, 3002
- Pro neznámé RC je použit fallback:
  - CZ: `RC <cislo> – Kontrola`
  - EN: `RC <number> - Check`

## Kritické / Nekritické rozdělení

Mapování stavů je v `severity.py`:

- **Kritické / Critical**:
  - `Fehler`
  - `Nicht in Ordnung`
- **Nekritické / Non-critical**:
  - `Warnung`
  - `Zu prüfen`

## Jak funguje CZ/EN výstup

- České listy obsahují i samostatné sloupce `Typ objektu` a `Číslo drátu`.
- Anglické listy obsahují i samostatné sloupce `Object type` a `Wire number`.
- `Leitungsnummer` je mapováno jako `Číslo drátu` (nikoliv `Číslo vedení`).

- Parser vytváří interní datový model (`IssueRecord`) v `excel_parser.py`.
- Teprve z interního modelu vznikají DataFrame pro:
  - `Prehled_CZ` (česky)
  - `Overview_EN` (anglicky)
- Překlady hlaviček a textových labelů jsou centralizované v `translators.py`.
- Listy jsou jazykově konzistentní (bez mixu čeština/angličtina/němčina).

## Formátování výstupu

- Tmavě modrá hlavička, bílý tučný text
- Autofilter
- Freeze top row
- Automatická šířka sloupců
- Zalomení textu ve sloupci detailu chyby
- Kritické řádky světle červené
- Nekritické řádky světle žluté

## Omezení projektu

- Některé reporty používají podmíněné formátování; proto logika **nespoléhá** na čtení červené barvy písma.
- Nástroj používá mapované relevantní sloupce dle RC.
- Názvy sloupců se mohou mezi verzemi reportů lišit; pro speciální varianty je vhodné doplnit mapování/handler.
- U složitých RC lze přidat vlastní handler v parseru (např. skupinová agregace jako RC 121).

## Testy

```bash
python -m unittest discover -s tests
```
