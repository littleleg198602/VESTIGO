import tempfile
import unittest
from pathlib import Path

from main import _discover_input_workbooks


class TestInputDiscovery(unittest.TestCase):
    def test_discovers_rulechecker_workbooks_recursively(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            nested_input = root / "Rulechecker" / "Rulechecker"
            nested_input.mkdir(parents=True)
            expected = nested_input / "PrfBer_TAB019708C_LTGS_KSK_RL_290001.xlsx"
            expected.write_text("", encoding="utf-8")

            (root / "BOM").mkdir()
            (root / "BOM" / "BOM.xlsx").write_text("", encoding="utf-8")
            (root / "HISTORY").mkdir()
            (root / "HISTORY" / "historie.xlsx").write_text("", encoding="utf-8")
            (root / "prehled_chyb_RC_svazek_rozklik_v2.xlsx").write_text("", encoding="utf-8")
            (nested_input / "~$temporary.xlsx").write_text("", encoding="utf-8")

            self.assertEqual(_discover_input_workbooks(root), [expected])


if __name__ == "__main__":
    unittest.main()
