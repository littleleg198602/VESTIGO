import tempfile
import unittest
from pathlib import Path

import pandas as pd

from history_lookup import build_history_map, note_split_for_rc


class TestHistoryOtherOverviews(unittest.TestCase):
    def test_generated_overview_history_is_kept_in_separate_column(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            history_dir = Path(tmp_dir) / "HISTORY"
            history_dir.mkdir()
            overview = history_dir / "VESTIGO_Prehled chyb SK_VW 271 TAB.019.728.xlsx"
            pd.DataFrame([
                {
                    "RC": 106,
                    "Název chyby": "PKO, WCS downcrease from 0,5 to 0,35",
                    "Notes": "Vyřešeno v jiném výkresu.",
                    "HISTORY_EXCEL": "původní poznámka",
                }
            ]).to_excel(overview, index=False)

            history_map = build_history_map(history_dir)
            excel_note, mail_note, overview_note = note_split_for_rc(history_map, 106)

            self.assertEqual(excel_note, "")
            self.assertEqual(mail_note, "")
            self.assertIn("Historie z jiného přehledu", overview_note)
            self.assertIn("PKO, WCS downcrease", overview_note)
            self.assertIn("Vyřešeno v jiném výkresu", overview_note)
            self.assertIn("file://", overview_note)


if __name__ == "__main__":
    unittest.main()
