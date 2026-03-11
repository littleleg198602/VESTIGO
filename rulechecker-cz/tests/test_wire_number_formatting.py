import unittest

import pandas as pd

from excel_parser import parse_rc_sheet
from rc_maps import get_rc_definition


class TestWireNumberFormatting(unittest.TestCase):
    def test_splits_concatenated_wire_numbers_into_new_lines(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Fehler",
                "Leitungsnummer": "4315443155",
                "Sonderleitung": "SL-1",
                "Leitungen": "43154 43155",
            }
        ])

        records = parse_rc_sheet(df, 110, get_rc_definition(110))

        self.assertEqual(records[0].wire_number, "43154\n43155")

    def test_replaces_delimiters_with_new_lines(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Fehler",
                "Leitungsnummer": "43154,43155",
                "Sonderleitung": "SL-1",
                "Leitungen": "43154 43155",
            }
        ])

        records = parse_rc_sheet(df, 110, get_rc_definition(110))

        self.assertEqual(records[0].wire_number, "43154\n43155")


    def test_prefers_multi_wire_source_when_available(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Fehler",
                "Leitungsnummer": "4316543166",
                "Leitungen": "43165 43166",
                "Sonderleitung": "SL-1",
            }
        ])

        records = parse_rc_sheet(df, 110, get_rc_definition(110))

        self.assertEqual(records[0].wire_number, "43165\n43166")

    def test_splits_numeric_string_with_decimal_suffix(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Fehler",
                "Leitungsnummer": "4316543166.0",
                "Sonderleitung": "SL-1",
                "Leitungen": "43165 43166",
            }
        ])

        records = parse_rc_sheet(df, 110, get_rc_definition(110))

        self.assertEqual(records[0].wire_number, "43165\n43166")

    def test_uses_connector_endpoint_when_wire_number_missing(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Fehler",
                "Leitungsnummer": "-",
                "Endpunkt": "X1/12",
                "Startpunkt": "T1/1",
            }
        ])

        records = parse_rc_sheet(df, 115, get_rc_definition(115))

        self.assertEqual(records[0].wire_number, "X1\n12")

    def test_uses_stecker_name_when_wire_number_missing(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Nicht in Ordnung",
                "Stecker": "XA.GX1.1_XA.GX1.2",
            }
        ])

        records = parse_rc_sheet(df, 115, get_rc_definition(115))

        self.assertEqual(records[0].wire_number, "XA.GX1.1_XA.GX1.2")


if __name__ == "__main__":
    unittest.main()
