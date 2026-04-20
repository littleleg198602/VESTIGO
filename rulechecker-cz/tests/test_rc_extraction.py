import unittest

from utils import extract_harness_name, extract_rc_number


class TestRCExtraction(unittest.TestCase):
    def test_extract_rc_number(self):
        self.assertEqual(extract_rc_number("1_LIN-Bus_Leitungsvorgabe"), 1)
        self.assertEqual(extract_rc_number("3002_Check"), 3002)
        self.assertIsNone(extract_rc_number("overview"))

    def test_extract_harness_name(self):
        self.assertEqual(
            extract_harness_name("PrfBer_TAB019727AC_STF_VORNE_191225_2025-12-10-102256"),
            "TAB019727AC_STF_VORNE",
        )
        self.assertEqual(extract_harness_name("custom_file_name"), "custom_file_name")


if __name__ == "__main__":
    unittest.main()
