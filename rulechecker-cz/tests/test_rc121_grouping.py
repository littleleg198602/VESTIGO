import unittest

import pandas as pd

from excel_parser import parse_rc_sheet
from rc_maps import get_rc_definition


class TestRC121Grouping(unittest.TestCase):
    def test_grouped_by_splice_and_vobes(self):
        df = pd.DataFrame(
            [
                {
                    "Einschätzung": "Nicht in Ordnung",
                    "Splice": "SP_FBASS",
                    "VOBES-ID": "A45",
                    "Leitungsnummer": "23001",
                    "Farbe Ist": "sw",
                    "Farbe Soll": "sw",
                    "Potential": "S.MU_FBASS..SVS2",
                },
                {
                    "Einschätzung": "Nicht in Ordnung",
                    "Splice": "SP_FBASS",
                    "VOBES-ID": "A45",
                    "Leitungsnummer": "23002",
                    "Farbe Ist": "sw/vi",
                    "Farbe Soll": "sw",
                    "Potential": "S.MU_FBASS..SVS2",
                },
            ]
        )
        out = parse_rc_sheet(df, 121, get_rc_definition(121))
        self.assertEqual(len(out), 1)
        self.assertIn("Dotčené dráty = 23001, 23002", out[0].where_cz)
        self.assertIn("Affected wires = 23001, 23002", out[0].where_en)

    def test_falls_back_to_splice_identifier_when_wires_missing(self):
        df = pd.DataFrame(
            [
                {
                    "Einschätzung": "Nicht in Ordnung",
                    "Splice": "SP_TEST",
                    "VOBES-ID": "V01",
                    "Farbe Ist": "sw",
                    "Farbe Soll": "sw",
                }
            ]
        )
        out = parse_rc_sheet(df, 121, get_rc_definition(121))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].wire_number, "SP_TEST")


if __name__ == "__main__":
    unittest.main()
