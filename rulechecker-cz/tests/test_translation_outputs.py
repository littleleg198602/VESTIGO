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

    def test_legacy_inspired_frame_columns_and_values(self):
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
        legacy = frames["LegacyInspired_EN"]

        self.assertEqual(legacy.columns.tolist(), [
            "Number of mistake",
            "Type of part",
            "Name of correction",
            "Task",
            "Area",
            "Priority",
            "Status",
            "note",
        ])
        self.assertEqual(legacy.iloc[0]["Number of mistake"], "RC 1")
        self.assertEqual(legacy.iloc[0]["Priority"], "Warning")
        self.assertEqual(legacy.iloc[0]["Status"], "done")


if __name__ == "__main__":
    unittest.main()
