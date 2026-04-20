from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

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
    "Čeho se týká",
    "Kde je chyba",
    "Doporučení",
    "Priority",
    "Progress",
    "Solution",
]
EN_COLUMNS = [
    "Harness name",
    "Severity",
    "RC",
    "Object type",
    "Identifier",
    "Error title",
    "Explanation",
    "Affected object",
    "Where is the issue",
    "Recommendation",
    "Priority",
    "Progress",
    "Solution",
]

def _legacy_priority(severity_en: str) -> str:
    return "Not OK" if severity_en == "Critical" else "Warning"

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
            "Čeho se týká": r.affected_cz,
            "Kde je chyba": r.where_cz,
            "Doporučení": _compose_recommendation(r.affected_cz, r.where_cz, r.recommendation_cz),
            "Priority": _legacy_priority(r.severity_en),
            "Progress": "",
            "Solution": "",
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
            "Affected object": r.affected_en,
            "Where is the issue": r.where_en,
            "Recommendation": _compose_recommendation(r.affected_en, r.where_en, r.recommendation_en),
            "Priority": _legacy_priority(r.severity_en),
            "Progress": "",
            "Solution": "",
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
            _format_sheet(ws, sheet)


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
        cell.hyperlink = f"{record.source_file}#'{record.source_sheet}'!A{record.source_row}"
        cell.style = "Hyperlink"


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

    where_col_name = "Kde je chyba" if "CZ" in sheet_name else "Where is the issue"
    wire_col_name = "Identifikátor" if "CZ" in sheet_name else "Identifier"
    where_col_idx = None
    wire_col_idx = None
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == where_col_name:
            where_col_idx = idx
        if cell.value == wire_col_name:
            wire_col_idx = idx

    critical_row_idx = 0
    non_critical_row_idx = 0
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        lead_value = str(row[0].value or "")
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

        if where_col_idx:
            row[where_col_idx - 1].alignment = Alignment(wrap_text=True, vertical="top")
        if wire_col_idx:
            row[wire_col_idx - 1].alignment = Alignment(wrap_text=True, vertical="top")

        if max_lines > 1:
            ws.row_dimensions[row[0].row].height = 15 * max_lines
