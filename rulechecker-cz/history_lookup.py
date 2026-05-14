from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
from rc_maps import RC_DEFINITIONS

RC_RE = re.compile(r"\b(?:rc|check|prüfung|prufung)\s*[:#-]?\s*(\d{1,4})\b", re.IGNORECASE)
INVALID_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
CHECK_BLOCK_RE = re.compile(r"check\s*(\d{1,4})\s*[:\-]?\s*(.+)", re.IGNORECASE)

RC_HEADERS = {"number of mistake", "prufung", "prüfung", "rc", "check"}
NOTE_HEADERS = {"note", "poznamka", "poznámka", "komentar", "komentář", "comment"}


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


def _history_link(path: Path) -> str:
    return f"[{path.name}]({path.resolve().as_uri()})"


def _norm(text: str) -> str:
    text = _clean_excel_text(text).lower()
    return text.replace("_", " ").strip()


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

        header_row_idx, rc_col, note_col = _detect_note_layout(df)
        if header_row_idx is not None and rc_col is not None and note_col is not None:
            for _, row in df.iloc[header_row_idx + 1 :].iterrows():
                rc_text = _clean_excel_text(str(row.iloc[rc_col] if rc_col < len(row) else ""))
                note_text = _clean_excel_text(str(row.iloc[note_col] if note_col < len(row) else ""))
                if not rc_text or not note_text or note_text.lower() == "nan":
                    continue
                for rc in _extract_rcs(rc_text):
                    out[rc].append(f"{_history_link(path)} {note_text[:180]}")
            continue

        # Bez rozpoznaných sloupců RC/Note data raději přeskočíme, aby
        # nevznikaly falešné přiřazení RC (např. RC1 z běžných čísel v textu).
        continue


def _detect_note_layout(df: pd.DataFrame) -> tuple[int | None, int | None, int | None]:
    for ridx in range(min(20, len(df.index))):
        vals = [str(v) for v in df.iloc[ridx].tolist()]
        norm = [_norm(v) for v in vals]
        rc_col = next((i for i, v in enumerate(norm) if v in RC_HEADERS), None)
        note_col = next((i for i, v in enumerate(norm) if v in NOTE_HEADERS), None)
        if rc_col is not None and note_col is not None:
            return ridx, rc_col, note_col
    return None, None, None


def _load_msg_history(path: Path, out: dict[int, list[str]]) -> None:
    try:
        text = path.read_bytes().decode("utf-8", errors="ignore")
    except Exception:
        return

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
            out[rc].append(f"{_history_link(path)} {msg[:180]}")

def _extract_rcs(text: str) -> set[int]:
    result = set()
    known_rcs = set(RC_DEFINITIONS.keys())
    for m in RC_RE.finditer(text):
        try:
            rc = int(m.group(1))
        except ValueError:
            continue
        if rc in known_rcs:
            result.add(rc)
    return result


def note_for_rc(history_map: dict[int, list[str]], rc: int) -> str:
    entries = history_map.get(rc, [])
    if not entries:
        return ""
    unique = []
    seen = set()
    seen_files = set()
    for e in entries:
        if e in seen:
            continue
        m = re.match(r"\[([^\]]+)\]\(", e)
        file_key = m.group(1).lower() if m else ""
        if file_key and file_key in seen_files:
            continue
        seen.add(e)
        if file_key:
            seen_files.add(file_key)
        unique.append(e)
    return "\n".join(unique[:5])


def _clean_excel_text(text: str) -> str:
    text = INVALID_CHAR_RE.sub("", text)
    return " ".join(text.split())
