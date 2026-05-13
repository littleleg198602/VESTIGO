from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

RC_RE = re.compile(r"\b(?:RC\s*)?(\d{1,4})\b", re.IGNORECASE)
INVALID_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


def build_history_map(history_dir: Path) -> dict[int, list[str]]:
    notes: dict[int, list[str]] = defaultdict(list)
    if not history_dir.exists() or not history_dir.is_dir():
        return {}

    for file in sorted(history_dir.iterdir()):
        suffix = file.suffix.lower()
        if suffix in {".xlsx", ".xls"}:
            _load_excel_history(file, notes)
        elif suffix == ".msg":
            _load_msg_history(file, notes)

    return {rc: vals for rc, vals in notes.items() if vals}


def _load_excel_history(path: Path, out: dict[int, list[str]]) -> None:
    try:
        xls = pd.ExcelFile(path, engine="openpyxl")
    except Exception:
        return

    for sheet in xls.sheet_names:
        try:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
        except Exception:
            continue
        for _, row in df.iterrows():
            vals = [str(v).strip() for v in row.tolist() if str(v).strip() and str(v).strip().lower() != "nan"]
            if not vals:
                continue
            line = " | ".join(vals)
            for rc in _extract_rcs(line):
                out[rc].append(_clean_excel_text(f"[{path.name}] {line[:220]}"))


def _load_msg_history(path: Path, out: dict[int, list[str]]) -> None:
    try:
        text = path.read_bytes().decode("utf-8", errors="ignore")
    except Exception:
        return
    compact = " ".join(text.split())
    for rc in _extract_rcs(compact):
        out[rc].append(_clean_excel_text(f"[{path.name}] {compact[:220]}"))


def _extract_rcs(text: str) -> set[int]:
    result = set()
    for m in RC_RE.finditer(text):
        try:
            rc = int(m.group(1))
        except ValueError:
            continue
        if 1 <= rc <= 9999:
            result.add(rc)
    return result


def note_for_rc(history_map: dict[int, list[str]], rc: int) -> str:
    entries = history_map.get(rc, [])
    if not entries:
        return ""
    unique = []
    seen = set()
    for e in entries:
        if e in seen:
            continue
        seen.add(e)
        unique.append(e)
    return "\n".join(unique[:5])


def _clean_excel_text(text: str) -> str:
    text = INVALID_CHAR_RE.sub("", text)
    return " ".join(text.split())
