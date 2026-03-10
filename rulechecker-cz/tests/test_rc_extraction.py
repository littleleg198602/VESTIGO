import unittest

from utils import extract_rc_number


class TestRCExtraction(unittest.TestCase):
    def test_extract_rc_number(self):
        self.assertEqual(extract_rc_number("1_LIN-Bus_Leitungsvorgabe"), 1)
        self.assertEqual(extract_rc_number("3002_Check"), 3002)
        self.assertIsNone(extract_rc_number("overview"))


if __name__ == "__main__":
    unittest.main()
