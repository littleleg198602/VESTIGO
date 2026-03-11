import unittest

from translators import translate_value


class TestMessageValueTranslation(unittest.TestCase):
    def test_translates_known_german_message_fragments(self):
        source = "Der Winkel muss größer als 30° sein. Verknüpfte Accessories: AK_005"

        cz = translate_value("Meldung", source, "cz")
        en = translate_value("Meldung", source, "en")

        self.assertIn("Úhel musí být větší než 30°.", cz)
        self.assertIn("Propojené příslušenství", cz)
        self.assertIn("The angle must be greater than 30°.", en)
        self.assertIn("Linked accessories", en)



    def test_translates_splice_bundle_length_sentence(self):
        source = "Bündellänge am Splice darf nicht länger als 100 mm sein"

        cz = translate_value("Meldung", source, "cz")
        en = translate_value("Meldung", source, "en")

        self.assertIn("Délka svazku na spoji nesmí být delší než 100 mm", cz)
        self.assertIn("Bundle length at splice must not exceed 100 mm", en)

if __name__ == "__main__":
    unittest.main()
