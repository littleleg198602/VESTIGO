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


if __name__ == "__main__":
    unittest.main()
