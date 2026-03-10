import unittest

from excel_parser import IssueRecord
from formatter import build_output_frames


class TestTranslationOutputs(unittest.TestCase):
    def test_cz_en_frames_from_single_model(self):
        record = IssueRecord(
            rc=106,
            severity_cz="Kritické",
            severity_en="Critical",
            title_cz="Shoda barvy vodiče a signálu",
            title_en="Wire and signal color consistency",
            explanation_cz="CZ vysvětlení",
            explanation_en="EN explanation",
            affected_cz="Leitung 385",
            affected_en="Leitung 385",
            where_cz="Skutečná barva (IST) = br/sw",
            where_en="Actual color (IST) = br/sw",
            recommendation_cz="CZ doporučení",
            recommendation_en="EN recommendation",
        )

        frames = build_output_frames([record])
        cz = frames["Prehled_CZ"]
        en = frames["Overview_EN"]

        self.assertEqual(cz.iloc[0]["Název chyby"], "Shoda barvy vodiče a signálu")
        self.assertEqual(en.iloc[0]["Error title"], "Wire and signal color consistency")


if __name__ == "__main__":
    unittest.main()
