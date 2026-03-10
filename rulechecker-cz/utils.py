from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from config import OUTPUT_PATTERN_HINTS

RC_SHEET_RE = re.compile(r"^(?P<rc>\d+)_")


def extract_rc_number(sheet_name: str) -> int | None:
    match = RC_SHEET_RE.match(sheet_name.strip())
    return int(match.group("rc")) if match else None


def is_generated_output_file(path: Path) -> bool:
    name_lower = path.name.lower()
    return any(hint in name_lower for hint in OUTPUT_PATTERN_HINTS)


def build_output_filename(input_file: Path, output_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = input_file.stem
    candidate = output_dir / f"{stem}__prehled_CZ_EN__{timestamp}.xlsx"
    if not candidate.exists():
        return candidate

    idx = 1
    while True:
        fallback = output_dir / f"{stem}__prehled_CZ_EN__{timestamp}__{idx:02d}.xlsx"
        if not fallback.exists():
            return fallback
        idx += 1
