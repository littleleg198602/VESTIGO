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
  - `LegacyInspired_EN` (anglický list inspirovaný dřívějším "Prehled chyb" formátem)

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

### Spouštěč bez příkazové řádky (Windows)

V adresáři projektu je připraven soubor `Spustit_RuleChecker.bat`.
Stačí na něj dvojkliknout a nástroj se spustí automaticky.

- Pokud existuje `.venv\Scripts\python.exe`, použije se virtuální prostředí.
- Jinak se použije `python` z PATH.
- Po doběhnutí se okno ponechá otevřené (`pause`), aby bylo vidět, zda vše proběhlo v pořádku.

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

- České listy obsahují i samostatné sloupce `Typ objektu`, `Identifikátor`, `Priority`, `Progress`, `Solution`.
- Anglické listy obsahují i samostatné sloupce `Object type`, `Identifier`, `Priority`, `Progress`, `Solution`.
- `Leitungsnummer` je mapováno do obecného sloupce `Identifikátor` (pro vyhledání čísla drátu, názvu konektoru nebo jiného klíče objektu).

- Parser vytváří interní datový model (`IssueRecord`) v `excel_parser.py`.
- Teprve z interního modelu vznikají DataFrame pro:
  - `Prehled_CZ` (česky)
  - `Overview_EN` (anglicky)
- Překlady hlaviček a textových labelů jsou centralizované v `translators.py`.
- Listy jsou jazykově konzistentní (bez mixu čeština/angličtina/němčina).

- Nový list `LegacyInspired_EN` přidává známé sloupce z historické šablony:
  - `Number of mistake`, `Type of part`, `Name of correction`, `Task`, `Area`, `Priority`, `Status`, `note`
  - `Priority` je mapované z vážnosti (`Critical -> Not OK`, `Non-critical -> Warning`)
  - `Status` je orientačně předvyplněn (`Critical -> in progress`, `Non-critical -> done`)

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
