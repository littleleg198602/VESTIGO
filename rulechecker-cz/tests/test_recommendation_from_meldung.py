import unittest

import pandas as pd

from excel_parser import parse_rc_sheet
from rc_maps import get_rc_definition


class TestRecommendationFromMeldung(unittest.TestCase):
    def test_recommendation_uses_only_translated_meldung(self):
        df = pd.DataFrame([
            {
                "Einschätzung": "Nicht in Ordnung",
                "Bauteil": "XA.810.1",
                "VOBES-ID": "",
                "Verwendungsstelle": "810.1",
                "Meldung": "Verpolung ist unbekannt.",
            }
        ])

        record = parse_rc_sheet(df, 338, get_rc_definition(338))[0]

        self.assertEqual(record.recommendation_cz, "Přepólování je neznámé.")
        self.assertEqual(record.recommendation_en, "Reverse polarity is unknown.")


if __name__ == "__main__":
    unittest.main()
