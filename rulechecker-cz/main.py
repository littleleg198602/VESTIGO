from __future__ import annotations

import argparse
import logging
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import INPUT_DIR, OUTPUT_DIR
from excel_parser import parse_workbook
from formatter import write_output_excel
from utils import build_output_filename, is_generated_output_file


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("rulechecker")


def run(input_dir: Path, output_dir: Path) -> tuple[int, list[Path]]:
    files = sorted(input_dir.glob("*.xlsx"))
    processed: list[Path] = []
    for file in files:
        if is_generated_output_file(file):
            LOG.info("Přeskakuji vygenerovaný výstup: %s", file.name)
            continue

        LOG.info("Zpracovávám: %s", file.name)
        records = parse_workbook(file)
        out_path = build_output_filename(file, output_dir)
        write_output_excel(out_path, records)
        LOG.info("Vytvořen výstup: %s (záznamů: %d)", out_path.name, len(records))
        processed.append(out_path)

    return len(processed), processed


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
