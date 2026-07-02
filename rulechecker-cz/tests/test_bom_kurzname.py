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

            self.assertEqual(_resolve_kurzname(mapping, "XA.VX57.4"), "CONN_A")
            self.assertEqual(_resolve_kurzname(mapping, "XA.GX1.1_XA.GX1.2"), "CONN_B, CONN_C")


if __name__ == "__main__":
    unittest.main()
