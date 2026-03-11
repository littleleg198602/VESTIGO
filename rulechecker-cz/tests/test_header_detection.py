import unittest

import pandas as pd

from excel_parser import _dataframe_from_raw_sheet, _detect_header_row, _extract_sheet_metadata, _make_unique_headers, _resolve_status_column


class TestHeaderDetection(unittest.TestCase):
    def test_detect_header_row_with_offset(self):
        raw = pd.DataFrame(
            [
                ["Prüfbericht", None, None],
                [None, None, None],
                ["Leitungsnummer", "Einschätzung", "Meldung"],
                ["123", "Fehler", "x"],
            ]
        )
        self.assertEqual(_detect_header_row(raw), 2)

    def test_resolve_status_alias(self):
        df = pd.DataFrame(columns=["Leitungsnummer", "Bewertung", "Meldung"])
        self.assertEqual(_resolve_status_column(df), "Bewertung")


    def test_extract_sheet_metadata_name_and_description(self):
        raw = pd.DataFrame(
            [
                ["Prüfung:", "1007", None],
                ["Name:", "Datenqualität: Überprüfung der Verwendungsstelle des Connectors", None],
                ["Beschreibung:", "Prüft, ob beim Connector eine Verwendungsstelle angegeben wird.", None],
                [None, None, None],
                ["Einschätzung", "Meldung", "Bauteil"],
                ["Nicht in Ordnung", "x", "XA.1"],
            ]
        )

        name, description = _extract_sheet_metadata(raw)
        self.assertIn("Verwendungsstelle des Connectors", name)
        self.assertIn("Connector", description)

        df = _dataframe_from_raw_sheet(raw)
        self.assertEqual(df.columns.tolist(), ["Einschätzung", "Meldung", "Bauteil"])

    def test_make_unique_headers(self):
        headers = ["A", "A", "", "A"]
        self.assertEqual(_make_unique_headers(headers), ["A", "A__1", "col_3", "A__2"])


if __name__ == "__main__":
    unittest.main()
