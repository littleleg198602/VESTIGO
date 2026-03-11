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

        self.assertEqual(records[0].wire_number, "T1/1 -> X1/12")

    def test_uses_stecker_name_when_wire_number_missing(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Nicht in Ordnung",
                "Stecker": "XA.GX1.1_XA.GX1.2",
            }
        ])

        records = parse_rc_sheet(df, 115, get_rc_definition(115))

        self.assertEqual(records[0].wire_number, "XA.GX1.1_XA.GX1.2")


    def test_uses_first_non_empty_stecker_when_duplicate_headers_exist(self):
        row = {
            "Einschätzung": "Nicht in Ordnung",
            "Stecker": "XA.GX1.1_XA.GX1.2",
            "Stecker__1": "-",
        }
        records = parse_rc_sheet(pd.DataFrame([row]), 115, get_rc_definition(115))
        self.assertEqual(records[0].wire_number, "XA.GX1.1_XA.GX1.2")

    def test_uses_sicherung_name_for_fuse_rows(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Nicht in Ordnung",
                "Sicherungsname": "SI_LVIR_F16",
                "Sicherungstyp": "Type_C",
            }
        ])

        records = parse_rc_sheet(df, 610, get_rc_definition(610))

        self.assertEqual(records[0].wire_number, "SI_LVIR_F16")



    def test_does_not_return_nan_as_identifier(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Nicht in Ordnung",
                "Leitungsnummer": float("nan"),
                "VOBES-ID": float("nan"),
                "Bauteil": "XA.810.1",
            }
        ])

        records = parse_rc_sheet(df, 338, get_rc_definition(338))

        self.assertEqual(records[0].wire_number, "XA.810.1")

if __name__ == "__main__":
    unittest.main()
