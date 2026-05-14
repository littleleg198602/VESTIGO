from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import quote

import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

from config import (
    OUTPUT_SHEET_CZ,
    OUTPUT_SHEET_EN,
)
from excel_parser import IssueRecord

CZ_COLUMNS = [
    "Název svazku",
    "Závažnost",
    "RC",
    "Typ objektu",
    "Identifikátor",
    "Název chyby",
    "Vysvětlení",
    "Doporučení",
    "Priority",
    "Progress",
    "Solution",
    "HISTORY",
    "HISTORY_LINK_1",
    "HISTORY_LINK_2",
    "HISTORY_LINK_3",
    "HISTORY_LINK_4",
    "HISTORY_LINK_5",
]
EN_COLUMNS = [
    "Harness name",
    "Severity",
    "RC",
    "Object type",
    "Identifier",
    "Error title",
    "Explanation",
    "Recommendation",
    "Priority",
    "Progress",
    "Solution",
    "HISTORY",
    "HISTORY_LINK_1",
    "HISTORY_LINK_2",
    "HISTORY_LINK_3",
    "HISTORY_LINK_4",
    "HISTORY_LINK_5",
]


def _history_link_columns(history_note: str) -> dict[str, str]:
    lines = [line.strip() for line in history_note.splitlines() if line.strip()]
    out = {}
    for idx in range(5):
        out[f"HISTORY_LINK_{idx + 1}"] = lines[idx] if idx < len(lines) else ""
    return out

def _legacy_priority(severity_en: str) -> str:
    return "Not OK" if severity_en == "Critical" else "Warning"


def _default_progress(severity_en: str) -> str:
    return "in progress" if severity_en == "Critical" else "done"


HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True)
CRITICAL_FILLS = [
    PatternFill("solid", fgColor="FDE2E4"),
    PatternFill("solid", fgColor="F8C8CD"),
    PatternFill("solid", fgColor="F5B5BC"),
    PatternFill("solid", fgColor="F29CA7"),
]
NON_CRITICAL_FILLS = [
    PatternFill("solid", fgColor="FFF9DB"),
    PatternFill("solid", fgColor="FFF3BF"),
    PatternFill("solid", fgColor="FFEC99"),
    PatternFill("solid", fgColor="FFE066"),
]
ROW_BORDER = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9"),
)


def _pick_fill(severity: str, row_idx: int) -> PatternFill:
    palette = CRITICAL_FILLS if severity in {"Kritické", "Critical", "Not OK"} else NON_CRITICAL_FILLS
    return palette[row_idx % len(palette)]


def build_output_frames(records: list[IssueRecord]) -> dict[str, pd.DataFrame]:
    cz_rows = [
        {
            "Název svazku": r.harness_name,
            "Závažnost": r.severity_cz,
            "RC": r.rc,
            "Typ objektu": r.object_type_cz,
            "Identifikátor": r.wire_number,
            "Název chyby": r.title_cz,
            "Vysvětlení": r.explanation_cz,
            "Doporučení": _compose_recommendation(r.affected_cz, r.where_cz, r.recommendation_cz),
            "Priority": _legacy_priority(r.severity_en),
            "Progress": _default_progress(r.severity_en),
            "Solution": "",
            "HISTORY": r.history_note,
            **_history_link_columns(r.history_note),
        }
        for r in records
    ]
    en_rows = [
        {
            "Harness name": r.harness_name,
            "Severity": r.severity_en,
            "RC": r.rc,
            "Object type": r.object_type_en,
            "Identifier": r.wire_number,
            "Error title": r.title_en,
            "Explanation": r.explanation_en,
            "Recommendation": _compose_recommendation(r.affected_en, r.where_en, r.recommendation_en),
            "Priority": _legacy_priority(r.severity_en),
            "Progress": _default_progress(r.severity_en),
            "Solution": "",
            "HISTORY": r.history_note,
            **_history_link_columns(r.history_note),
        }
        for r in records
    ]

    cz_df = pd.DataFrame(cz_rows, columns=CZ_COLUMNS)
    en_df = pd.DataFrame(en_rows, columns=EN_COLUMNS)

    return {
        OUTPUT_SHEET_CZ: cz_df,
        OUTPUT_SHEET_EN: en_df,
    }


def _compose_recommendation(affected: str, where: str, recommendation: str) -> str:
    return f"{affected}; {where}; {recommendation}".strip("; ").strip()


def write_output_excel(out_path: Path, records: list[IssueRecord]) -> None:
    frames = build_output_frames(records)
    records_by_sheet = _split_records_by_sheet(records)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet, df in frames.items():
            df.to_excel(writer, sheet_name=sheet, index=False)

        for sheet in frames:
            ws = writer.book[sheet]
            _add_rc_hyperlinks(ws, records_by_sheet.get(sheet, []))
            _add_history_hyperlinks(ws)
            _add_history_link_columns_hyperlinks(ws)
            _format_sheet(ws, sheet)
            _add_priority_validation(ws)
            _add_progress_validation(ws)


def _split_records_by_sheet(records: list[IssueRecord]) -> dict[str, list[IssueRecord]]:
    return {
        OUTPUT_SHEET_CZ: records,
        OUTPUT_SHEET_EN: records,
    }


def _add_rc_hyperlinks(ws, sheet_records: list[IssueRecord]) -> None:
    rc_col_idx = None
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == "RC":
            rc_col_idx = idx
            break

    if rc_col_idx is None:
        return

    for row_idx, record in enumerate(sheet_records, start=2):
        if row_idx > ws.max_row:
            break
        cell = ws.cell(row=row_idx, column=rc_col_idx)
        source_uri = Path(record.source_file).resolve().as_uri()
        sheet_ref = quote(record.source_sheet, safe="")
        cell.hyperlink = f"{source_uri}#'{sheet_ref}'!A{record.source_row}"
        cell.style = "Hyperlink"




def _add_history_hyperlinks(ws) -> None:
    history_col_idx = None
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == "HISTORY":
            history_col_idx = idx
            break

    if history_col_idx is None:
        return

    for row_idx in range(2, ws.max_row + 1):
        cell = ws.cell(row=row_idx, column=history_col_idx)
        text = str(cell.value or "")
        m = re.search(r"\[([^\]]+)\]\((file://[^)]+)\)", text)
        if not m:
            continue

        cleaned = re.sub(r"\[([^\]]+)\]\((file://[^)]+)\)", r"[\1]", text)
        cell.value = cleaned
        cell.hyperlink = m.group(2)
        cell.style = "Hyperlink"


def _add_history_link_columns_hyperlinks(ws) -> None:
    cols = []
    for idx, cell in enumerate(ws[1], start=1):
        if str(cell.value).startswith("HISTORY_LINK_"):
            cols.append(idx)

    for col_idx in cols:
        for row_idx in range(2, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            text = str(cell.value or "")
            m = re.search(r"\[([^\]]+)\]\((file://[^)]+)\)", text)
            if not m:
                continue
            cleaned = re.sub(r"\[([^\]]+)\]\((file://[^)]+)\)", r"[\1]", text)
            cell.value = cleaned
            cell.hyperlink = m.group(2)
            cell.style = "Hyperlink"

def _add_priority_validation(ws) -> None:
    priority_col_idx = None
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == "Priority":
            priority_col_idx = idx
            break
    if priority_col_idx is None or ws.max_row < 2:
        return

    priority_col_letter = ws.cell(row=1, column=priority_col_idx).column_letter
    validation = DataValidation(type="list", formula1='"1,2,3,4,5"', allow_blank=True)
    ws.add_data_validation(validation)
    validation.add(f"{priority_col_letter}2:{priority_col_letter}{ws.max_row}")


def _add_progress_validation(ws) -> None:
    progress_col_idx = None
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == "Progress":
            progress_col_idx = idx
            break
    if progress_col_idx is None or ws.max_row < 2:
        return

    progress_col_letter = ws.cell(row=1, column=progress_col_idx).column_letter
    validation = DataValidation(type="list", formula1='"start,in progress,N/A,done"', allow_blank=True)
    ws.add_data_validation(validation)
    validation.add(f"{progress_col_letter}2:{progress_col_letter}{ws.max_row}")


def _format_sheet(ws, sheet_name: str) -> None:
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for col in ws.columns:
        max_len = max(len(str(c.value or "")) for c in col)
        ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 14), 60)

    wire_col_name = "Identifikátor" if "CZ" in sheet_name else "Identifier"
    severity_col_name = "Závažnost" if "CZ" in sheet_name else "Severity"
    wire_col_idx = None
    severity_col_idx = None
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == wire_col_name:
            wire_col_idx = idx
        if cell.value == severity_col_name:
            severity_col_idx = idx

    critical_row_idx = 0
    non_critical_row_idx = 0
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        severity_value = ""
        if severity_col_idx:
            severity_value = str(row[severity_col_idx - 1].value or "")
        lead_value = severity_value
        if lead_value in {"Kritické", "Critical"}:
            fill = _pick_fill(lead_value, critical_row_idx)
            critical_row_idx += 1
        else:
            fill = _pick_fill(lead_value, non_critical_row_idx)
            non_critical_row_idx += 1

        max_lines = 1
        for cell in row:
            cell.fill = fill
            cell.border = ROW_BORDER
            cell.alignment = Alignment(vertical="top")
            line_count = str(cell.value or "").count("\n") + 1
            if line_count > max_lines:
                max_lines = line_count

        if wire_col_idx:
            row[wire_col_idx - 1].alignment = Alignment(wrap_text=True, vertical="top")

        if max_lines > 1:
            ws.row_dimensions[row[0].row].height = 15 * max_lines
