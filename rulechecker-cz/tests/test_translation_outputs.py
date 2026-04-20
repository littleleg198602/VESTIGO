import unittest

from excel_parser import IssueRecord
from formatter import build_output_frames


class TestTranslationOutputs(unittest.TestCase):
    def test_cz_en_frames_from_single_model(self):
        record = IssueRecord(
            rc=106,
            severity_cz="Kritické",
            severity_en="Critical",
            title_cz="Shoda barvy drátu a signálu",
            title_en="Wire and signal color consistency",
            explanation_cz="CZ vysvětlení",
            explanation_en="EN explanation",
            object_type_cz="Drát",
            object_type_en="Wire",
            wire_number="385",
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

        self.assertEqual(cz.iloc[0]["Identifikátor"], "385")
        self.assertEqual(cz.iloc[0]["Název chyby"], "Shoda barvy drátu a signálu")
        self.assertEqual(en.iloc[0]["Object type"], "Wire")
        self.assertEqual(en.iloc[0]["Error title"], "Wire and signal color consistency")
        self.assertEqual(cz.iloc[0]["Priority"], "Not OK")
        self.assertEqual(cz.iloc[0]["Progress"], "")
        self.assertEqual(cz.iloc[0]["Solution"], "")
        self.assertEqual(en.iloc[0]["Priority"], "Not OK")
        self.assertEqual(en.iloc[0]["Progress"], "")
        self.assertEqual(en.iloc[0]["Solution"], "")

    def test_output_contains_only_cz_en_overview_sheets(self):
        record = IssueRecord(
            rc=1,
            severity_cz="Nekritické",
            severity_en="Non-critical",
            title_cz="Kontrola",
            title_en="Check",
            explanation_cz="CZ",
            explanation_en="EN task",
            object_type_cz="Vodič",
            object_type_en="Wire",
            wire_number="100",
            affected_cz="A",
            affected_en="A",
            where_cz="B",
            where_en="B",
            recommendation_cz="CZ rec",
            recommendation_en="Use same WCS",
        )

        frames = build_output_frames([record])
        self.assertEqual(set(frames.keys()), {"Prehled_CZ", "Overview_EN"})


if __name__ == "__main__":
    unittest.main()
