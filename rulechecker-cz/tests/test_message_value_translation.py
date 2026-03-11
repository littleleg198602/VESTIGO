import unittest

from translators import translate_metadata_text, translate_value


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


    def test_translates_lin_grounding_messages(self):
        source = (
            "Stecker hat keine Masseleitung. Teilnehmer des LIN-Busses sind mit unterschiedlichen "
            "Massebolzen verbunden."
        )

        cz = translate_value("Meldung", source, "cz")
        en = translate_value("Meldung", source, "en")

        self.assertIn("Konektor nemá zemnicí vedení.", cz)
        self.assertIn("Účastníci LIN sběrnice jsou připojeni na různé zemnící body.", cz)
        self.assertIn("Connector has no ground wire.", en)
        self.assertIn("LIN bus participants are connected to different ground points.", en)


    def test_translates_sheet_metadata_text(self):
        name = "Splice: Überprüfung der Bündellänge am Splice"
        desc = "Prüft, ob die maximale Bündellänge am Splice eingehalten wird."

        self.assertIn("kontrola", translate_metadata_text(name, "cz").lower())
        self.assertIn("check", translate_metadata_text(name, "en").lower())
        self.assertIn("maximální délka svazku", translate_metadata_text(desc, "cz").lower())
        self.assertIn("maximum bundle length", translate_metadata_text(desc, "en").lower())


    def test_translates_sheet_metadata_ascii_variants(self):
        name = "Leitung: Ueberpruefung der Laengendifferenz zwischen den Sonderleitungscores"
        desc = "Prueft, ob die maximale Buendellaenge am Splice eingehalten wird."

        self.assertIn("kontrola rozdílu délky", translate_metadata_text(name, "cz").lower())
        self.assertIn("length difference", translate_metadata_text(name, "en").lower())
        self.assertIn("maximální délka svazku", translate_metadata_text(desc, "cz").lower())
        self.assertIn("maximum bundle length", translate_metadata_text(desc, "en").lower())

if __name__ == "__main__":
    unittest.main()
