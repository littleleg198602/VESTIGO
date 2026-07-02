import tempfile
import unittest
from pathlib import Path

from main import _load_kurzname_map, _resolve_kurzname


class TestBomKurzname(unittest.TestCase):
    def test_loads_kurzname_from_bom_csv_in_input_bom_folder(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            bom = root / "BOM"
            bom.mkdir()
            (bom / "AEM_TAB019708C_0335.BOM.csv").write_text(
                "Bauteil;Kurzname\nXA.VX57.4;CONN_A\nXA.GX1.1;CONN_B\nXA.GX1.2;CONN_C\n",
                encoding="utf-8",
            )

            mapping = _load_kurzname_map(root)

            self.assertTrue((bom / "AEM_TAB019708C_0335.BOM.xlsx").exists())
            self.assertEqual(_resolve_kurzname(mapping, "XA.VX57.4"), "CONN_A")
            self.assertEqual(_resolve_kurzname(mapping, "XA.GX1.1_XA.GX1.2"), "CONN_B, CONN_C")

    def test_converts_and_reads_any_semicolon_csv_in_bom_folder(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            bom = root / "BOM"
            bom.mkdir()
            (bom / "AEM_TAB019708C_0335.Wirelist.csv").write_text(
                "Bauteil;Kurzname\nXA.G483.1;CONN_WIRELIST\n",
                encoding="utf-8",
            )

            mapping = _load_kurzname_map(root)

            self.assertTrue((bom / "AEM_TAB019708C_0335.Wirelist.xlsx").exists())
            self.assertEqual(_resolve_kurzname(mapping, "XA.G483.1"), "CONN_WIRELIST")

    def test_converts_ragged_semicolon_csv_to_xlsx(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            bom = root / "BOM"
            bom.mkdir()
            (bom / "AEM_TAB019709C_0323.BOM.csv").write_text(
                "Bauteil;Kurzname\nXA.V5.4;CONN_SHORT;extra\nXA.VX57.3;CONN_NORMAL\n",
                encoding="utf-8",
            )

            mapping = _load_kurzname_map(root)

            self.assertTrue((bom / "AEM_TAB019709C_0323.BOM.xlsx").exists())
            self.assertEqual(_resolve_kurzname(mapping, "XA.V5.4"), "CONN_SHORT")
            self.assertEqual(_resolve_kurzname(mapping, "XA.VX57.3"), "CONN_NORMAL")


if __name__ == "__main__":
    unittest.main()
