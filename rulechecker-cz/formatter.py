from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from config import (
    CRITICAL_SHEET_CZ,
    CRITICAL_SHEET_EN,
    NON_CRITICAL_SHEET_CZ,
    NON_CRITICAL_SHEET_EN,
    OUTPUT_SHEET_CZ,
    OUTPUT_SHEET_EN,
)
from excel_parser import IssueRecord

CZ_COLUMNS = [
    "Závažnost",
    "RC",
    "Typ objektu",
    "Číslo drátu",
    "Název chyby",
    "Vysvětlení",
    "Čeho se týká",
    "Kde je chyba",
    "Doporučení",
]
EN_COLUMNS = [
    "Severity",
    "RC",
    "Object type",
    "Wire number",
    "Error title",
    "Explanation",
    "Affected object",
    "Where is the issue",
    "Recommendation",
]

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True)
CRITICAL_FILL = PatternFill("solid", fgColor="F8D7DA")
NON_CRITICAL_FILL = PatternFill("solid", fgColor="FFF3CD")


def build_output_frames(records: list[IssueRecord]) -> dict[str, pd.DataFrame]:
    cz_rows = [
        {
            "Závažnost": r.severity_cz,
            "RC": r.rc,
            "Typ objektu": r.object_type_cz,
            "Číslo drátu": r.wire_number,
            "Název chyby": r.title_cz,
            "Vysvětlení": r.explanation_cz,
            "Čeho se týká": r.affected_cz,
            "Kde je chyba": r.where_cz,
            "Doporučení": r.recommendation_cz,
        }
        for r in records
    ]
    en_rows = [
        {
            "Severity": r.severity_en,
            "RC": r.rc,
            "Object type": r.object_type_en,
            "Wire number": r.wire_number,
            "Error title": r.title_en,
            "Explanation": r.explanation_en,
            "Affected object": r.affected_en,
            "Where is the issue": r.where_en,
            "Recommendation": r.recommendation_en,
        }
        for r in records
    ]

    cz_df = pd.DataFrame(cz_rows, columns=CZ_COLUMNS)
    en_df = pd.DataFrame(en_rows, columns=EN_COLUMNS)

    return {
        OUTPUT_SHEET_CZ: cz_df,
        OUTPUT_SHEET_EN: en_df,
        CRITICAL_SHEET_CZ: cz_df[cz_df["Závažnost"] == "Kritické"],
        CRITICAL_SHEET_EN: en_df[en_df["Severity"] == "Critical"],
        NON_CRITICAL_SHEET_CZ: cz_df[cz_df["Závažnost"] == "Nekritické"],
        NON_CRITICAL_SHEET_EN: en_df[en_df["Severity"] == "Non-critical"],
    }


def write_output_excel(out_path: Path, records: list[IssueRecord]) -> None:
    frames = build_output_frames(records)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet, df in frames.items():
            df.to_excel(writer, sheet_name=sheet, index=False)

        for sheet in frames:
            ws = writer.book[sheet]
            _format_sheet(ws, sheet)


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
    where_col_idx = None
    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == where_col_name:
            where_col_idx = idx
            break

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        severity = str(row[0].value or "")
        fill = CRITICAL_FILL if severity in {"Kritické", "Critical"} else NON_CRITICAL_FILL
        for cell in row:
            cell.fill = fill
            cell.alignment = Alignment(vertical="top")
        if where_col_idx:
            row[where_col_idx - 1].alignment = Alignment(wrap_text=True, vertical="top")
