from __future__ import annotations

import argparse
import logging
from pathlib import Path

from config import INPUT_DIR, OUTPUT_DIR
from excel_parser import parse_workbook
from formatter import write_output_excel
from utils import build_output_filename, is_generated_output_file


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("rulechecker")


def run(input_dir: Path, output_dir: Path) -> None:
    files = sorted(input_dir.glob("*.xlsx"))
    for file in files:
        if is_generated_output_file(file):
            LOG.info("Přeskakuji vygenerovaný výstup: %s", file.name)
            continue

        LOG.info("Zpracovávám: %s", file.name)
        records = parse_workbook(file)
        out_path = build_output_filename(file, output_dir)
        write_output_excel(out_path, records)
        LOG.info("Vytvořen výstup: %s (záznamů: %d)", out_path.name, len(records))


def main() -> None:
    parser = argparse.ArgumentParser(description="RuleChecker CZ/EN overview generator")
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR, help="Adresář se vstupními .xlsx reporty")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Adresář pro výstupy")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
