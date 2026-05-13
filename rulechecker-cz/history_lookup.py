from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

RC_RE = re.compile(r"\b(?:RC\s*)?(\d{1,4})\b", re.IGNORECASE)
INVALID_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
<<<<<<< codex/add-input-output-configuration-interface-ffyimg
CHECK_BLOCK_RE = re.compile(r"check\s*(\d{1,4})\s*[:\-]?\s*(.+)", re.IGNORECASE)

RC_HEADERS = {"number of mistake", "prufung", "prüfung", "rc", "check"}
NOTE_HEADERS = {"note", "poznamka", "poznámka", "komentar", "komentář", "comment"}
=======
>>>>>>> main


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


<<<<<<< codex/add-input-output-configuration-interface-ffyimg
def _norm(text: str) -> str:
    text = _clean_excel_text(text).lower()
    return text.replace("_", " ").strip()


=======
>>>>>>> main
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
<<<<<<< codex/add-input-output-configuration-interface-ffyimg

        header_row_idx, rc_col, note_col = _detect_note_layout(df)
        if header_row_idx is None or rc_col is None or note_col is None:
            continue

        for _, row in df.iloc[header_row_idx + 1 :].iterrows():
            rc_text = _clean_excel_text(str(row.iloc[rc_col] if rc_col < len(row) else ""))
            note_text = _clean_excel_text(str(row.iloc[note_col] if note_col < len(row) else ""))
            if not rc_text or not note_text or note_text.lower() == "nan":
                continue
            for rc in _extract_rcs(rc_text):
                out[rc].append(f"[{path.name}] {note_text[:180]}")


def _detect_note_layout(df: pd.DataFrame) -> tuple[int | None, int | None, int | None]:
    for ridx in range(min(20, len(df.index))):
        vals = [str(v) for v in df.iloc[ridx].tolist()]
        norm = [_norm(v) for v in vals]
        rc_col = next((i for i, v in enumerate(norm) if v in RC_HEADERS), None)
        note_col = next((i for i, v in enumerate(norm) if v in NOTE_HEADERS), None)
        if rc_col is not None and note_col is not None:
            return ridx, rc_col, note_col
    return None, None, None
=======
        for _, row in df.iterrows():
            vals = [str(v).strip() for v in row.tolist() if str(v).strip() and str(v).strip().lower() != "nan"]
            if not vals:
                continue
            line = " | ".join(vals)
            for rc in _extract_rcs(line):
                out[rc].append(_clean_excel_text(f"[{path.name}] {line[:220]}"))
>>>>>>> main


def _load_msg_history(path: Path, out: dict[int, list[str]]) -> None:
    try:
        text = path.read_bytes().decode("utf-8", errors="ignore")
    except Exception:
        return
<<<<<<< codex/add-input-output-configuration-interface-ffyimg

    lines = [_clean_excel_text(line) for line in text.splitlines()]
    for i, line in enumerate(lines):
        m = CHECK_BLOCK_RE.search(line)
        if not m:
            continue
        rc = int(m.group(1))
        msg = m.group(2).strip()
        if not msg and i + 1 < len(lines):
            msg = lines[i + 1].strip()
        if msg:
            out[rc].append(f"[{path.name}] {msg[:180]}")
=======
    compact = " ".join(text.split())
    for rc in _extract_rcs(compact):
        out[rc].append(_clean_excel_text(f"[{path.name}] {compact[:220]}"))
>>>>>>> main


def _extract_rcs(text: str) -> set[int]:
    result = set()
    for m in RC_RE.finditer(text):
<<<<<<< codex/add-input-output-configuration-interface-ffyimg
        rc = int(m.group(1))
=======
        try:
            rc = int(m.group(1))
        except ValueError:
            continue
>>>>>>> main
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
<<<<<<< codex/add-input-output-configuration-interface-ffyimg
    return "\n".join(unique[:3])
=======
    return "\n".join(unique[:5])
>>>>>>> main


def _clean_excel_text(text: str) -> str:
    text = INVALID_CHAR_RE.sub("", text)
    return " ".join(text.split())
