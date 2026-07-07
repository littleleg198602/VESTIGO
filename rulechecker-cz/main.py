from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from config import INPUT_DIR, OUTPUT_DIR
from excel_parser import parse_workbook
from formatter import write_output_excel
from history_lookup import build_history_map, note_for_rc, note_split_for_rc
from utils import build_aggregate_output_filename, is_generated_output_file


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("rulechecker")


def run(input_dir: Path, output_dir: Path) -> tuple[int, list[Path]]:
    files = _discover_input_workbooks(input_dir)
    all_records = []
    processed_inputs: list[Path] = []
    history_map = build_history_map(input_dir / "HISTORY")
    kurzname_map = _load_kurzname_map(input_dir)

    for file in files:
        if is_generated_output_file(file):
            LOG.info("Přeskakuji vygenerovaný výstup: %s", file.name)
            continue

        LOG.info("Zpracovávám: %s", file.name)
        records = parse_workbook(file)
        for rec in records:
            rec.history_note = note_for_rc(history_map, rec.rc)
            rec.history_excel, rec.history_mail, rec.history_other_overviews = note_split_for_rc(history_map, rec.rc)
            rec.kurzname = _resolve_kurzname(kurzname_map, rec.wire_number)
        all_records.extend(records)
        processed_inputs.append(file)

    if not processed_inputs:
        LOG.info("Nebyly nalezeny žádné vstupní soubory ke zpracování.")
        return 0, []

    out_path = build_aggregate_output_filename(output_dir)
    write_output_excel(out_path, all_records)
    LOG.info("Vytvořen výstup: %s (záznamů: %d, vstupních souborů: %d)", out_path.name, len(all_records), len(processed_inputs))
    return 1, [out_path]


def _discover_input_workbooks(input_dir: Path) -> list[Path]:
    files: list[Path] = []
    for file in input_dir.rglob("*.xlsx"):
        if not file.is_file():
            continue
        if file.name.startswith("~$"):
            continue
        if is_generated_output_file(file):
            LOG.info("Přeskakuji vygenerovaný výstup: %s", file.name)
            continue
        relative_parts = {part.lower() for part in file.relative_to(input_dir).parts[:-1]}
        if relative_parts & {"bom", "history"}:
            LOG.info("Přeskakuji pomocný soubor mimo RuleChecker vstup: %s", file)
            continue
        files.append(file)
    return sorted(files)


def _load_kurzname_map(input_dir: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    bom_candidates = list(input_dir.glob("*BOM*.xlsx"))
    bom_dir = input_dir / "BOM"
    if bom_dir.exists():
        converted = _convert_bom_csv_files_to_xlsx(bom_dir)
        bom_candidates.extend(converted)
        bom_candidates.extend(sorted(bom_dir.rglob("*.xlsx")))

    for bom_file in sorted(set(bom_candidates)):
        try:
            xls = pd.ExcelFile(bom_file, engine="openpyxl")
        except Exception:
            continue
        for sheet in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet, header=None)
            except Exception:
                continue
            header_row = None
            key_cols: list[int] = []
            kurz_col = None
            for ridx in range(min(20, len(df.index))):
                row_key_cols: list[int] = []
                row_kurz_col = None
                row = [str(v).strip().lower() for v in df.iloc[ridx].tolist()]
                for cidx, val in enumerate(row):
                    if _is_kurzname_key_header(val):
                        row_key_cols.append(cidx)
                    if "kurzname" in val:
                        row_kurz_col = cidx
                if row_key_cols and row_kurz_col is not None:
                    header_row = ridx
                    key_cols = row_key_cols
                    kurz_col = row_kurz_col
                    break
            if header_row is None or not key_cols or kurz_col is None:
                # Fallback pro čitelné BOM XLSX se známým layoutem:
                # VOBES bývá ve sloupci B, Kurzname ve sloupci E.
                if len(df.columns) >= 5:
                    header_row = 2
                    key_cols = [1]
                    kurz_col = 4
                else:
                    continue
            for _, row in df.iloc[header_row + 1 :].iterrows():
                kurz = str(row.iloc[kurz_col] if kurz_col < len(row) else "").strip()
                if not kurz or kurz.lower() == "nan":
                    continue
                for key_col in key_cols:
                    if key_col >= len(row):
                        continue
                    _add_kurzname_mapping(mapping, row.iloc[key_col], kurz)
    return mapping


def _convert_bom_csv_files_to_xlsx(bom_dir: Path) -> list[Path]:
    converted: list[Path] = []
    for csv_path in sorted(bom_dir.rglob("*.csv")):
        xlsx_path = csv_path.with_suffix(".xlsx")
        if xlsx_path.exists() and xlsx_path.stat().st_mtime >= csv_path.stat().st_mtime:
            converted.append(xlsx_path)
            continue
        df = _read_semicolon_csv(csv_path)
        if df is None:
            LOG.warning("BOM CSV se nepodařilo převést na XLSX: %s", csv_path)
            continue
        try:
            df.to_excel(xlsx_path, index=False, header=False, engine="openpyxl")
        except Exception as exc:
            LOG.warning("BOM CSV se nepodařilo uložit jako XLSX %s: %s", xlsx_path, exc)
            continue
        converted.append(xlsx_path)
    return converted


def _read_semicolon_csv(path: Path) -> pd.DataFrame | None:
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                rows = list(csv.reader(handle, delimiter=";"))
        except Exception:
            continue
        if not rows:
            return pd.DataFrame()
        max_len = max(len(row) for row in rows)
        normalized_rows = [row + [""] * (max_len - len(row)) for row in rows]
        return pd.DataFrame(normalized_rows, dtype=str)
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "latin-1"):
        try:
            return pd.read_csv(path, sep=";", header=None, dtype=str, encoding=encoding, engine="python", on_bad_lines="warn")
        except Exception:
            continue
    return None


def _is_kurzname_key_header(header: str) -> bool:
    normalized = str(header).strip().lower()
    return any(
        token in normalized
        for token in {
            "vobes",
            "bauteil",
            "komponente",
            "connector",
            "stecker",
            "leitungsnummer",
            "leitung",
            "pin",
            "kammer",
        }
    )


def _add_kurzname_mapping(mapping: dict[str, str], key: object, kurz: str) -> None:
    text = str(key).strip()
    if not text or text.lower() == "nan":
        return
    mapping[text] = kurz
    norm = _normalize_vobes(text)
    if norm:
        mapping[norm] = kurz


def _normalize_vobes(value: str) -> str:
    text = str(value).strip().upper()
    m = re.search(r"\bX[AB]\.[A-Z0-9]+(?:\.[A-Z0-9]+)*\b", text)
    if m:
        return m.group(0)
    return text


def _resolve_kurzname(mapping: dict[str, str], identifier: str) -> str:
    raw = str(identifier).strip()
    if not raw:
        return ""
    if raw in mapping:
        return mapping[raw]
    norm = _normalize_vobes(raw)
    if norm in mapping:
        return mapping[norm]
    matches = []
    for part in re.split(r"[\s,;_/]+", raw):
        value = part.strip()
        if not value:
            continue
        match = mapping.get(value) or mapping.get(_normalize_vobes(value))
        if match and match not in matches:
            matches.append(match)
    return ", ".join(matches)



def run_gui(default_input_dir: Path, default_output_dir: Path) -> None:
    root = tk.Tk()
    root.title("RuleChecker CZ/EN")
    root.geometry("700x360")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    input_var = tk.StringVar(value=str(default_input_dir))
    output_var = tk.StringVar(value=str(default_output_dir))
    status_var = tk.StringVar(value="Vyber vstupní a výstupní složku, potom spusť zpracování.")

    def pick_input_dir() -> None:
        selected = filedialog.askdirectory(initialdir=input_var.get() or str(default_input_dir))
        if selected:
            input_var.set(selected)

    def pick_output_dir() -> None:
        selected = filedialog.askdirectory(initialdir=output_var.get() or str(default_output_dir))
        if selected:
            output_var.set(selected)

    def start_processing() -> None:
        input_dir = Path(input_var.get()).expanduser()
        output_dir = Path(output_var.get()).expanduser()

        if not input_dir.exists() or not input_dir.is_dir():
            messagebox.showerror("Chybný vstup", "Vstupní složka neexistuje nebo není složka.")
            return

        output_dir.mkdir(parents=True, exist_ok=True)
        count, outputs = run(input_dir, output_dir)

        status_lines = [
            f"Čteno ze složky: {input_dir}",
            f"Ukládáno do složky: {output_dir}",
            f"Vytvořeno výstupů: {count}",
        ]
        if outputs:
            preview = "\n".join(f"• {path.name}" for path in outputs[:5])
            status_lines.append(f"Poslední výstupy:\n{preview}")

        status_var.set("\n".join(status_lines))
        messagebox.showinfo("Hotovo", f"Zpracování dokončeno. Vytvořeno souborů: {count}")

    ttk.Label(frame, text="Vstupní složka (.xlsx soubory):").grid(row=0, column=0, sticky="w", pady=(0, 4))
    ttk.Entry(frame, textvariable=input_var, width=70).grid(row=1, column=0, sticky="we", padx=(0, 8))
    ttk.Button(frame, text="Vybrat...", command=pick_input_dir).grid(row=1, column=1, sticky="e")

    ttk.Label(frame, text="Výstupní složka:").grid(row=2, column=0, sticky="w", pady=(16, 4))
    ttk.Entry(frame, textvariable=output_var, width=70).grid(row=3, column=0, sticky="we", padx=(0, 8))
    ttk.Button(frame, text="Vybrat...", command=pick_output_dir).grid(row=3, column=1, sticky="e")

    ttk.Button(frame, text="Spustit zpracování", command=start_processing).grid(row=4, column=0, sticky="w", pady=(20, 10))

    ttk.Label(frame, text="Stav:").grid(row=5, column=0, sticky="w", pady=(8, 4))
    ttk.Label(frame, textvariable=status_var, justify="left").grid(row=6, column=0, columnspan=2, sticky="w")

    frame.columnconfigure(0, weight=1)
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="RuleChecker CZ/EN overview generator")
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR, help="Adresář se vstupními .xlsx reporty")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Adresář pro výstupy")
    parser.add_argument("--gui", action="store_true", help="Spustí jednoduchou obrazovku pro výběr složek")
    parser.add_argument("--cli", action="store_true", help="Vynutí konzolové zpracování bez GUI")
    args = parser.parse_args()

    if args.gui or not args.cli:
        run_gui(args.input_dir, args.output_dir)
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
