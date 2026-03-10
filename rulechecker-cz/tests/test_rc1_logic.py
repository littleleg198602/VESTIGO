import unittest

import pandas as pd

from excel_parser import parse_rc_sheet
from rc_maps import get_rc_definition


class TestRC1Logic(unittest.TestCase):
    def test_rc1_issue_text(self):
        df = pd.DataFrame(
            [
                {
                    "Einschätzung": "Fehler",
                    "Leitungsnummer": "385",
                    "Teilenummer der Leitung": "N_037_004_0",
                    "Prüfung Parameter": "N_108_151_05;N_108_151_06",
                }
            ]
        )
        out = parse_rc_sheet(df, 1, get_rc_definition(1))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].where_cz, "Číslo dílu drátu = N_037_004_0")
        self.assertEqual(out[0].where_en, "Wire part number = N_037_004_0")

    def test_rc1_accepts_case_and_spacing_variants_in_status(self):
        df = pd.DataFrame(
            [
                {
                    "Einschätzung": "  fehler ",
                    "Leitungsnummer": "385",
                    "Teilenummer der Leitung": "N_037_004_0",
                    "Prüfung Parameter": "N_108_151_05;N_108_151_06",
                }
            ]
        )
        out = parse_rc_sheet(df, 1, get_rc_definition(1))
        self.assertEqual(len(out), 1)


if __name__ == "__main__":
    unittest.main()
