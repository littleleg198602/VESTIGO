import unittest

import pandas as pd

from excel_parser import parse_rc_sheet
from formatter import build_output_frames
from rc_maps import get_rc_definition


class TestObjectTypeAndWireColumn(unittest.TestCase):
    def test_wire_number_and_object_type_present(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Fehler",
                "Leitungsnummer": "904138",
                "Teilenummer der Leitung": "N_037_004_0",
            }
        ])
        records = parse_rc_sheet(df, 1, get_rc_definition(1))
        self.assertEqual(records[0].wire_number, "904138")
        self.assertEqual(records[0].object_type_cz, "Drát")

        frames = build_output_frames(records)
        self.assertIn("Identifikátor", frames["Prehled_CZ"].columns)
        self.assertIn("Object type", frames["Overview_EN"].columns)



    def test_rc1005_reports_fuse_object_type(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Nicht in Ordnung",
                "Sicherungsname": "SI_LVIR_F16",
                "Sicherungstyp": "Type_C",
            }
        ])
        records = parse_rc_sheet(df, 1005, get_rc_definition(1005))
        self.assertEqual(records[0].object_type_cz, "Pojistka")
        self.assertEqual(records[0].wire_number, "SI_LVIR_F16")

if __name__ == "__main__":
    unittest.main()
