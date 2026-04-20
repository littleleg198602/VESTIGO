from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

import pandas as pd

from config import HEADER_STATUS_NAME
from rc_maps import RC_DEFINITIONS, RCDefinition, get_rc_definition
from severity import map_status_to_severity
from translators import clean_value, translate_header, translate_metadata_text, translate_value
from utils import extract_harness_name, extract_rc_number

LOG = logging.getLogger(__name__)

STATUS_HEADER_CANDIDATES = [
    "Einschätzung",
    "Einschaetzung",
    "Bewertung",
    "Status",
]


@dataclass
class IssueRecord:
    rc: int
    severity_cz: str
    severity_en: str
    title_cz: str
    title_en: str
    explanation_cz: str
    explanation_en: str
    object_type_cz: str
    object_type_en: str
    wire_number: str
    affected_cz: str
    affected_en: str
    where_cz: str
    where_en: str
    recommendation_cz: str
    recommendation_en: str
    harness_name: str = ""
    source_file: str = ""
    source_sheet: str = ""
    source_row: int = 1


def parse_workbook(path: Path) -> list[IssueRecord]:
    try:
        xls = pd.ExcelFile(path, engine="openpyxl")
    except Exception as exc:
        LOG.error("Nelze načíst soubor %s: %s", path, exc)
        return []

    records: list[IssueRecord] = []
    harness_name = extract_harness_name(path.stem)
    for sheet in xls.sheet_names:
        rc = extract_rc_number(sheet)
        if rc is None:
            continue

        raw = _read_sheet_raw(xls, sheet)
        if raw is None:
            continue

        sheet_name_value, sheet_description = _extract_sheet_metadata(raw)

        df = _dataframe_from_raw_sheet(raw)
        if df is None:
            continue

        status_col = _resolve_status_column(df)
        if not status_col:
            LOG.warning("List %s nemá rozpoznatelný sloupec stavu.", sheet)
            continue

        defn = _with_sheet_metadata(get_rc_definition(rc), sheet_name_value, sheet_description)
        records.extend(
            parse_rc_sheet(
                df,
                rc,
                defn,
                status_col,
                source_file=path.name,
                source_sheet=sheet,
                harness_name=harness_name,
            )
        )

    return records


def parse_rc_sheet(
    df: pd.DataFrame,
    rc: int,
    defn: RCDefinition,
    status_col: str = HEADER_STATUS_NAME,
    source_file: str = "",
    source_sheet: str = "",
    harness_name: str = "",
) -> list[IssueRecord]:
    severity_series = df[status_col].map(lambda value: map_status_to_severity(clean_value(value)))
    filtered = df[severity_series.notna()].copy()
    if filtered.empty:
        return []

    if defn.handler == "rc121":
        return _parse_rc121_grouped(filtered, rc, defn, status_col, source_file, source_sheet, harness_name)

    out: list[IssueRecord] = []
    for idx, row in filtered.iterrows():
        severity = severity_series.loc[idx]
        if not severity:
            continue
        source_row = _resolve_source_row(df, idx)
        out.append(
            _build_record_from_row(
                row,
                rc,
                defn,
                severity.cz,
                severity.en,
                source_file,
                source_sheet,
                source_row,
                harness_name,
            )
        )
    return out


def _parse_rc121_grouped(
    df: pd.DataFrame,
    rc: int,
    defn: RCDefinition,
    status_col: str,
    source_file: str,
    source_sheet: str,
    harness_name: str,
) -> list[IssueRecord]:
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
    for _, group in groups:
        first_group_idx = group.index[0]
        status = clean_value(group.iloc[0].get(status_col))
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
            f"VOBES-ID = {vobes_value}; Dotčené dráty = {', '.join(wires) or '-'}; "
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

        identifier = ", ".join(wires) if wires else (splice_name or vobes_value or "-")
        out.append(
            IssueRecord(
                rc=rc,
                harness_name=harness_name,
                severity_cz=severity.cz,
                severity_en=severity.en,
                title_cz=defn.title_cz,
                title_en=defn.title_en,
                explanation_cz=defn.explanation_cz,
                explanation_en=defn.explanation_en,
                object_type_cz=defn.object_type_cz,
                object_type_en=defn.object_type_en,
                wire_number=identifier,
                affected_cz=f"Splice {splice_name}".strip(),
                affected_en=f"Splice {splice_name}".strip(),
                where_cz=where_cz,
                where_en=where_en,
                recommendation_cz=defn.recommendation_cz,
                recommendation_en=defn.recommendation_en,
                source_file=source_file,
                source_sheet=source_sheet,
                source_row=_resolve_source_row(df, first_group_idx),
            )
        )
    return out


def _build_record_from_row(
    row: pd.Series,
    rc: int,
    defn: RCDefinition,
    severity_cz: str,
    severity_en: str,
    source_file: str,
    source_sheet: str,
    source_row: int,
    harness_name: str,
) -> IssueRecord:
    affected_cz = _compose_from_columns(row, defn.affected_columns, "cz")
    affected_en = _compose_from_columns(row, defn.affected_columns, "en")

    if defn.handler == "rc1":
        part_no = _first_non_empty_value(row, ["Teilenummer der Leitung", "Teilenummer", "Part number"])
        where_cz = f"Číslo dílu drátu = {part_no or '-'}"
        where_en = f"Wire part number = {part_no or '-'}"
    elif defn.handler == "rc106":
        ist = _first_non_empty_value(row, ["IST-Farbe", "Farbe Ist"])
        soll = _first_non_empty_value(row, ["SOLL-Farbe", "Farbe Soll"])
        match = _first_non_empty_value(row, ["Farben-Übereinstimmung", "Farbübereinstimmung"])
        where_cz = f"Skutečná barva (IST) = {ist or '-'}; Požadovaná barva (SOLL) = {soll or '-'}; Shoda barev = {match or '-'}"
        where_en = f"Actual color (IST) = {ist or '-'}; Required color (SOLL) = {soll or '-'}; Color match = {match or '-'}"
    else:
        where_cz = _compose_from_columns(row, defn.issue_columns, "cz")
        where_en = _compose_from_columns(row, defn.issue_columns, "en")

    wire_number = _extract_wire_number(row)

    return IssueRecord(
        rc=rc,
        harness_name=harness_name,
        severity_cz=severity_cz,
        severity_en=severity_en,
        title_cz=defn.title_cz,
        title_en=defn.title_en,
        explanation_cz=defn.explanation_cz,
        explanation_en=defn.explanation_en,
        object_type_cz=defn.object_type_cz,
        object_type_en=defn.object_type_en,
        wire_number=wire_number,
        affected_cz=affected_cz,
        affected_en=affected_en,
        where_cz=where_cz,
        where_en=where_en,
        recommendation_cz=defn.recommendation_cz,
        recommendation_en=defn.recommendation_en,
        source_file=source_file,
        source_sheet=source_sheet,
        source_row=source_row,
    )


def _compose_from_columns(row: pd.Series, columns: list[str], lang: str) -> str:
    chunks = []
    for col in columns:
        value = _first_non_empty_value(row, [col])
        if not value:
            continue
        translated = translate_header(col, lang)
        display_value = translate_value(col, value, lang)
        chunks.append(f"{translated} = {display_value}")
    return "; ".join(chunks) if chunks else "N/A"


def _read_sheet_raw(xls: pd.ExcelFile, sheet_name: str) -> pd.DataFrame | None:
    try:
        # raw načtení bez headeru pro detekci hlavičky i metadata v různých řádcích
        return pd.read_excel(xls, sheet_name=sheet_name, header=None)
    except Exception as exc:
        LOG.warning("Nelze načíst list %s: %s", sheet_name, exc)
        return None


def _dataframe_from_raw_sheet(raw: pd.DataFrame) -> pd.DataFrame | None:
    header_idx = _detect_header_row(raw)
    if header_idx is None:
        return None

    header_values = [clean_value(v) for v in raw.iloc[header_idx].tolist()]
    data = raw.iloc[header_idx + 1 :].copy()
    data.columns = _make_unique_headers(header_values)
    data = data.dropna(how="all")
    source_rows = list(data.index + 1)
    out = data.reset_index(drop=True)
    out.attrs["source_rows"] = source_rows
    return out


def _resolve_source_row(df: pd.DataFrame, idx: int) -> int:
    source_rows = df.attrs.get("source_rows")
    if not isinstance(source_rows, list):
        return int(idx) + 2
    if idx < 0 or idx >= len(source_rows):
        return int(idx) + 2
    return int(source_rows[idx])


def _safe_read_rc_sheet(xls: pd.ExcelFile, sheet_name: str) -> pd.DataFrame | None:
    raw = _read_sheet_raw(xls, sheet_name)
    if raw is None:
        return None
    return _dataframe_from_raw_sheet(raw)


def _extract_sheet_metadata(raw: pd.DataFrame) -> tuple[str, str]:
    name = ""
    description = ""

    max_rows = min(len(raw), 80)
    for idx in range(max_rows):
        row_values = [clean_value(v) for v in raw.iloc[idx].tolist() if clean_value(v)]
        if not row_values:
            continue

        row_text = " ".join(row_values)
        row_text_norm = _normalize_header(row_text)

        if row_text_norm.startswith("name:") and not name:
            name = _extract_metadata_value(row_values)
        elif row_text_norm.startswith("beschreibung:") and not description:
            description = _extract_metadata_value(row_values)

        if name and description:
            break

    return name, description


def _extract_metadata_value(values: list[str]) -> str:
    if not values:
        return ""
    joined = " ".join(values).strip()
    if ":" not in joined:
        return joined
    return joined.split(":", 1)[1].strip()


def _with_sheet_metadata(defn: RCDefinition, name: str, description: str) -> RCDefinition:
    if defn.rc in RC_DEFINITIONS:
        return defn

    if not name and not description:
        return defn

    title_base = name or defn.title_cz
    explanation_base = description or defn.explanation_cz
    if defn.handler == "rc1":
        return replace(
            defn,
            title_cz=translate_metadata_text(title_base, "cz"),
            title_en=translate_metadata_text(title_base, "en"),
            explanation_cz=defn.explanation_cz,
            explanation_en=defn.explanation_en,
        )
    return replace(
        defn,
        title_cz=translate_metadata_text(title_base, "cz"),
        title_en=translate_metadata_text(title_base, "en"),
        explanation_cz=translate_metadata_text(explanation_base, "cz"),
        explanation_en=translate_metadata_text(explanation_base, "en"),
    )


def _detect_header_row(raw: pd.DataFrame) -> int | None:
    max_rows = min(len(raw), 80)
    for idx in range(max_rows):
        row = [clean_value(v) for v in raw.iloc[idx].tolist()]
        if _row_contains_status_header(row):
            return idx
    return None


def _row_contains_status_header(row_values: list[str]) -> bool:
    normalized = {_normalize_header(v) for v in row_values if v}
    for candidate in STATUS_HEADER_CANDIDATES:
        if _normalize_header(candidate) in normalized:
            return True
    return False


def _resolve_status_column(df: pd.DataFrame) -> str | None:
    normalized_map = {_normalize_header(str(c)): str(c) for c in df.columns}
    for candidate in STATUS_HEADER_CANDIDATES:
        key = _normalize_header(candidate)
        if key in normalized_map:
            return normalized_map[key]
    # fallback na původní název kvůli kompatibilitě
    if HEADER_STATUS_NAME in df.columns:
        return HEADER_STATUS_NAME
    return None


def _make_unique_headers(headers: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    result: list[str] = []
    for idx, h in enumerate(headers):
        base = h or f"col_{idx + 1}"
        count = counts.get(base, 0)
        if count == 0:
            result.append(base)
        else:
            result.append(f"{base}__{count}")
        counts[base] = count + 1
    return result


def _normalize_header(value: str) -> str:
    return " ".join((value or "").replace("\n", " ").lower().split())


def _find_col(columns: Iterable[str], candidates: list[str]) -> str | None:
    lowered = {_normalize_header(str(c)): str(c) for c in columns}
    for candidate in candidates:
        col = lowered.get(_normalize_header(candidate))
        if col is not None:
            return str(col)
    return None


def _unique_values(df: pd.DataFrame, candidates: list[str]) -> list[str]:
    col = _find_col(df.columns, candidates)
    if col is None:
        return []
    values = [clean_value(v) for v in df[col].tolist()]
    return sorted({v for v in values if v})




def _extract_wire_number(row: pd.Series) -> str:
    start_point = _extract_identifier_value(row, ["Startpunkt"]) 
    end_point = _extract_identifier_value(row, ["Endpunkt"])
    if start_point and end_point:
        return f"{start_point} -> {end_point}"

    normalized_columns = [
        "Leitungsnummer",
        "Leitung",
        "Leitungen",
        "Wire number",
    ]
    normalized_values: list[str] = []
    for candidate in normalized_columns:
        key = _first_available_key(row, [candidate])
        if not key:
            continue
        value = _normalize_wire_number(clean_value(row.get(key)))
        if value and value != "-":
            normalized_values.append(value)

    if normalized_values:
        for value in normalized_values:
            if "\n" in value:
                return value
        return normalized_values[0]

    preserve_columns = [
        "Stecker",
        "Bauteil",
        "Steckername",
        "Connector",
        "Sicherungsname",
        "Sicherungsträger",
        "Sicherungsplatz",
        "Sicherungstyp",
        "Signalname",
        "Signal",
        "Komponente",
        "Sonderleitung",
        "Splice",
        "VOBES-ID",
        "Verwendungsstelle",
        "Potential",
    ]
    for column in preserve_columns:
        value = _extract_identifier_value(row, [column])
        if value:
            return value

    return "-"


def _extract_identifier_value(row: pd.Series, candidates: list[str]) -> str:
    value = _first_non_empty_value(row, candidates)
    if not value or value == "-":
        return ""
    return value


def _normalize_wire_number(value: str) -> str:
    if not value:
        return "-"

    separators = ["\n", ";", ",", "|", "/", "\\", "\t"]
    normalized = value
    for sep in separators:
        normalized = normalized.replace(sep, " ")
    parts = [part for part in normalized.split() if part]
    if len(parts) > 1:
        return "\n".join(parts)

    compact = parts[0] if parts else value
    if compact.endswith('.0') and compact.replace('.', '', 1).isdigit():
        compact = compact[:-2]

    if compact.isdigit() and len(compact) >= 10 and len(compact) % 2 == 0:
        half = len(compact) // 2
        return f"{compact[:half]}\n{compact[half:]}"

    return compact or "-"

def _first_available_key(row: pd.Series, candidates: list[str]) -> str | None:
    for candidate in candidates:
        normalized_candidate = _normalize_header(candidate)
        for key in row.index:
            normalized_key = _normalize_header(str(key))
            if normalized_key == normalized_candidate or normalized_key.startswith(f"{normalized_candidate}__"):
                return str(key)
    return None


def _first_non_empty_value(row: pd.Series, candidates: list[str]) -> str:
    for candidate in candidates:
        normalized_candidate = _normalize_header(candidate)
        for key in row.index:
            normalized_key = _normalize_header(str(key))
            if normalized_key != normalized_candidate and not normalized_key.startswith(f"{normalized_candidate}__"):
                continue
            value = clean_value(row.get(key))
            if value and value != "-":
                return value
    return ""
