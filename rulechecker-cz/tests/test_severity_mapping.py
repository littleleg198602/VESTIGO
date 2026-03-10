import unittest

from severity import map_status_to_severity


class TestSeverityMapping(unittest.TestCase):
    def test_severity_mapping(self):
        self.assertEqual(map_status_to_severity("Fehler").cz, "Kritické")
        self.assertEqual(map_status_to_severity("Nicht in Ordnung").en, "Critical")
        self.assertEqual(map_status_to_severity("Warnung").cz, "Nekritické")
        self.assertEqual(map_status_to_severity("Zu prüfen").en, "Non-critical")
        self.assertEqual(map_status_to_severity("  fehler ").cz, "Kritické")
        self.assertEqual(map_status_to_severity("Not OK").en, "Critical")
        self.assertEqual(map_status_to_severity("warning").cz, "Nekritické")
        self.assertIsNone(map_status_to_severity("In Ordnung"))


if __name__ == "__main__":
    unittest.main()
