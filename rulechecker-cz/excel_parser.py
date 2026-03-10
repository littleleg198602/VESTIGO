from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from config import HEADER_PARAM_NAME, HEADER_STATUS_NAME, PROBLEM_STATUSES
from rc_maps import RCDefinition, get_rc_definition
from severity import map_status_to_severity
from translators import clean_value, translate_header
from utils import extract_rc_number

LOG = logging.getLogger(__name__)


@dataclass
class IssueRecord:
    rc: int
    severity_cz: str
    severity_en: str
    title_cz: str
    title_en: str
    explanation_cz: str
    explanation_en: str
    affected_cz: str
    affected_en: str
    where_cz: str
    where_en: str
    recommendation_cz: str
    recommendation_en: str


def parse_workbook(path: Path) -> list[IssueRecord]:
    try:
        xls = pd.ExcelFile(path, engine="openpyxl")
    except Exception as exc:
        LOG.error("Nelze načíst soubor %s: %s", path, exc)
        return []

    records: list[IssueRecord] = []
    for sheet in xls.sheet_names:
        rc = extract_rc_number(sheet)
        if rc is None:
            continue
        df = _safe_read_sheet(xls, sheet)
        if df is None or HEADER_STATUS_NAME not in df.columns:
            continue
        defn = get_rc_definition(rc)
        records.extend(parse_rc_sheet(df, rc, defn))
    return records


def parse_rc_sheet(df: pd.DataFrame, rc: int, defn: RCDefinition) -> list[IssueRecord]:
    filtered = df[df[HEADER_STATUS_NAME].astype(str).str.strip().isin(PROBLEM_STATUSES)].copy()
    if filtered.empty:
        return []

    if defn.handler == "rc121":
        return _parse_rc121_grouped(filtered, rc, defn)

    out: list[IssueRecord] = []
    for _, row in filtered.iterrows():
        severity = map_status_to_severity(clean_value(row.get(HEADER_STATUS_NAME)))
        if not severity:
            continue
        out.append(_build_record_from_row(row, rc, defn, severity.cz, severity.en))
    return out


def _parse_rc121_grouped(df: pd.DataFrame, rc: int, defn: RCDefinition) -> list[IssueRecord]:
    key_splice = _find_col(df.columns, ["Splice", "Spleiß", "Splice-Name"])
    key_vobes = _find_col(df.columns, ["VOBES-ID", "VOBES"])
    if not key_splice:
        key_splice = "Splice"
        df[key_splice] = ""
    if not key_vobes:
        key_vobes = "VOBES-ID"
        df[key_vobes] = ""

    groups = df.groupby([key_splice, key_vobes], dropna=False)
    out: list[IssueRecord] = []
    for (_, _), group in groups:
        status = clean_value(group.iloc[0].get(HEADER_STATUS_NAME))
        severity = map_status_to_severity(status)
        if not severity:
            continue
        wires = _unique_values(group, ["Leitungsnummer", "Leitung"])
        color_ist = _unique_values(group, ["Farbe Ist", "IST-Farbe"])
        color_soll = _unique_values(group, ["Farbe Soll", "SOLL-Farbe"])
        potentials = _unique_values(group, ["Potential"])
        splice_name = clean_value(group.iloc[0].get(key_splice))
        vobes_value = clean_value(group.iloc[0].get(key_vobes))

        where_cz = (
            f"VOBES-ID = {vobes_value}; Dotčené vodiče = {', '.join(wires) or '-'}; "
            f"Skutečné barvy = {', '.join(color_ist) or '-'}; "
            f"Požadované barvy = {', '.join(color_soll) or '-'}; "
            f"Potenciály = {', '.join(potentials) or '-'}"
        )
        where_en = (
            f"VOBES-ID = {vobes_value}; Affected wires = {', '.join(wires) or '-'}; "
            f"Actual colors = {', '.join(color_ist) or '-'}; "
            f"Required colors = {', '.join(color_soll) or '-'}; "
            f"Potentials = {', '.join(potentials) or '-'}"
        )

        out.append(
            IssueRecord(
                rc=rc,
                severity_cz=severity.cz,
                severity_en=severity.en,
                title_cz=defn.title_cz,
                title_en=defn.title_en,
                explanation_cz=defn.explanation_cz,
                explanation_en=defn.explanation_en,
                affected_cz=f"Splice {splice_name}".strip(),
                affected_en=f"Splice {splice_name}".strip(),
                where_cz=where_cz,
                where_en=where_en,
                recommendation_cz=defn.recommendation_cz,
                recommendation_en=defn.recommendation_en,
            )
        )
    return out


def _build_record_from_row(
    row: pd.Series,
    rc: int,
    defn: RCDefinition,
    severity_cz: str,
    severity_en: str,
) -> IssueRecord:
    affected_cz = _compose_from_columns(row, defn.affected_columns, "cz")
    affected_en = _compose_from_columns(row, defn.affected_columns, "en")

    if defn.handler == "rc1":
        part_no = clean_value(row.get("Teilenummer der Leitung"))
        where_cz = f"Číslo dílu vodiče = {part_no}"
        where_en = f"Wire part number = {part_no}"
    elif defn.handler == "rc106":
        ist = clean_value(row.get("IST-Farbe"))
        soll = clean_value(row.get("SOLL-Farbe"))
        match = clean_value(row.get("Farben-Übereinstimmung"))
        where_cz = f"Skutečná barva (IST) = {ist}; Požadovaná barva (SOLL) = {soll}; Shoda barev = {match}"
        where_en = f"Actual color (IST) = {ist}; Required color (SOLL) = {soll}; Color match = {match}"
    elif defn.handler == "rc110":
        where_cz = _compose_from_columns(row, defn.issue_columns, "cz")
        where_en = _compose_from_columns(row, defn.issue_columns, "en")
    else:
        where_cz = _compose_from_columns(row, defn.issue_columns, "cz")
        where_en = _compose_from_columns(row, defn.issue_columns, "en")

    return IssueRecord(
        rc=rc,
        severity_cz=severity_cz,
        severity_en=severity_en,
        title_cz=defn.title_cz,
        title_en=defn.title_en,
        explanation_cz=defn.explanation_cz,
        explanation_en=defn.explanation_en,
        affected_cz=affected_cz,
        affected_en=affected_en,
        where_cz=where_cz,
        where_en=where_en,
        recommendation_cz=defn.recommendation_cz,
        recommendation_en=defn.recommendation_en,
    )


def _compose_from_columns(row: pd.Series, columns: list[str], lang: str) -> str:
    chunks = []
    for col in columns:
        value = clean_value(row.get(col))
        if not value:
            continue
        translated = translate_header(col, lang)
        chunks.append(f"{translated} = {value}")
    return "; ".join(chunks) if chunks else ("N/A" if lang == "en" else "N/A")


def _safe_read_sheet(xls: pd.ExcelFile, sheet_name: str) -> pd.DataFrame | None:
    try:
        return pd.read_excel(xls, sheet_name=sheet_name)
    except Exception as exc:
        LOG.warning("Nelze načíst list %s: %s", sheet_name, exc)
        return None


def _find_col(columns: Iterable[str], candidates: list[str]) -> str | None:
    lowered = {str(c).lower(): c for c in columns}
    for candidate in candidates:
        col = lowered.get(candidate.lower())
        if col is not None:
            return str(col)
    return None


def _unique_values(df: pd.DataFrame, candidates: list[str]) -> list[str]:
    col = _find_col(df.columns, candidates)
    if col is None:
        return []
    values = [clean_value(v) for v in df[col].tolist()]
    return sorted({v for v in values if v})
