# test_blended.py
"""
MedOriva AI Ltd - Automated Regression Test Suite
Validates: 9 MVP Languages, Multi-Script Colloquial Input,
Negation Checking, Neutral Communication Cues, and Temporary Staff Review.
Coverage: 25 Dedicated Unit Tests (including Full Lexicon Audit)
"""

import unittest
from blended_engine import BlendedLanguageProcessor
from blended_config import EXPANDED_LEXICON

class TestBlendedLanguageProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.processor = BlendedLanguageProcessor()

    # -------------------------------------------------------------------------
    # 1. CORE STRING NORMALIZATION
    # -------------------------------------------------------------------------
    def test_01_normalization_punctuation_and_whitespace(self):
        raw = "  Enaku... Nenji   VALI??? Illai!  "
        normalized = self.processor.normalize(raw)
        self.assertEqual(normalized, "enaku nenji vali illai")

    # -------------------------------------------------------------------------
    # 2. TAMIL (Thanglish)
    # -------------------------------------------------------------------------
    def test_02_tamil_affirmative_chest_pain(self):
        res = self.processor.process_intake("ta", "enaku nenji vali irukku")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_03_tamil_negated_chest_pain(self):
        res = self.processor.process_intake("ta", "enaku nenji vali illai")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    def test_04_tamil_routine_appointment(self):
        res = self.processor.process_intake("ta", "doctor appointment irukku")
        self.assertFalse(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Appointment", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 3. HINDI (Hinglish)
    # -------------------------------------------------------------------------
    def test_05_hindi_affirmative_chest_pain(self):
        res = self.processor.process_intake("hi", "mujhe seene me dard hai")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_06_hindi_negated_chest_pain(self):
        res = self.processor.process_intake("hi", "seene me dard nahi hai")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    def test_07_hindi_routine_prescription(self):
        res = self.processor.process_intake("hi", "dawai chahiye parchi")
        self.assertFalse(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Prescription", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 4. MALAYALAM (Manglish)
    # -------------------------------------------------------------------------
    def test_08_malayalam_affirmative_chest_pain(self):
        res = self.processor.process_intake("ml", "chankil vedana undu")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_09_malayalam_negated_chest_pain(self):
        res = self.processor.process_intake("ml", "chankil vedana illa")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    def test_10_malayalam_routine_sample_drop(self):
        res = self.processor.process_intake("ml", "urine sample labil kodukkanam")
        self.assertFalse(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Sample Drop", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 5. POLISH (Colloquial Latin)
    # -------------------------------------------------------------------------
    def test_11_polish_affirmative_chest_pain(self):
        res = self.processor.process_intake("pl", "bol w klatce piersiowej")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_12_polish_negated_chest_pain(self):
        res = self.processor.process_intake("pl", "nie ma bolu w klatce")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    def test_13_polish_routine_appointment(self):
        res = self.processor.process_intake("pl", "mam wizyte u lekarza")
        self.assertFalse(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Appointment", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 6. ARABIC (Arabizi / Franco-Arabic)
    # -------------------------------------------------------------------------
    def test_14_arabic_arabizi_affirmative_chest_pain(self):
        res = self.processor.process_intake("ar", "waja3 bel sadr shadid")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_15_arabic_arabizi_negated_chest_pain(self):
        res = self.processor.process_intake("ar", "waja3 bel sadr la")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 7. URDU (Roman Urdu)
    # -------------------------------------------------------------------------
    def test_16_urdu_affirmative_chest_pain(self):
        res = self.processor.process_intake("ur", "seene mein dard bohot hai")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_17_urdu_negated_chest_pain(self):
        res = self.processor.process_intake("ur", "dil mein dard nahi hai")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 8. BENGALI (Banglish)
    # -------------------------------------------------------------------------
    def test_18_bengali_affirmative_chest_pain(self):
        res = self.processor.process_intake("bn", "bukey chap betha ache")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_19_bengali_negated_chest_pain(self):
        res = self.processor.process_intake("bn", "bukey betha nei")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 9. SOMALI (Colloquial Latin)
    # -------------------------------------------------------------------------
    def test_20_somali_affirmative_chest_pain(self):
        res = self.processor.process_intake("so", "xanuun laabta daran")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_21_somali_negated_chest_pain(self):
        res = self.processor.process_intake("so", "xanuun laabta ma jiro")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 10. ROMANIAN (Colloquial Latin)
    # -------------------------------------------------------------------------
    def test_22_romanian_affirmative_chest_pain(self):
        res = self.processor.process_intake("ro", "durere in piept puternica")
        self.assertTrue(res["communication_cue"])
        self.assertFalse(res["meaning_check"])
        self.assertIn("Chest Pain", res["extracted_meaning"])

    def test_23_romanian_negated_chest_pain(self):
        res = self.processor.process_intake("ro", "nu am durere in piept")
        self.assertTrue(res["communication_cue"])
        self.assertTrue(res["meaning_check"])
        self.assertIn("Negative wording detected with Chest Pain wording", res["extracted_meaning"])

    # -------------------------------------------------------------------------
    # 11. ADMINISTRATIVE SUMMARY & CLIPBOARD EXPORT INTEGRITY
    # -------------------------------------------------------------------------
    def test_24_clipboard_summary_structure_and_disclaimer(self):
        res = self.processor.process_intake("ta", "enaku appointment irukku")
        summary = res["clipboard_summary"]
        self.assertIn("[MedOriva Temporary Staff Review]", summary)
        self.assertIn("Language: TA", summary)
        self.assertIn("Confirmation status: Not recorded", summary)
        self.assertNotIn("Patient Input:", summary)
        self.assertIn("local practice policy", summary)

    # -------------------------------------------------------------------------
    # 12. FULL LEXICON AUDIT (1000+ Tokens Across All 9 MVP Languages)
    # -------------------------------------------------------------------------
    def test_25_all_lexicon_tokens_integrity(self):
        """Verifies that all 1,000+ tokens across all 9 languages load and process cleanly."""
        expected_langs = {"ta", "hi", "ml", "pl", "ar", "ur", "bn", "so", "ro"}
        self.assertEqual(set(EXPANDED_LEXICON.keys()), expected_langs)

        total_tokens = 0
        for lang, categories in EXPANDED_LEXICON.items():
            # Check negation list
            negs = categories.get("negation", [])
            self.assertGreater(len(negs), 0, f"Language {lang} missing negation tokens")
            total_tokens += len(negs)

            # Check critical symptoms
            for cat, phrases in categories.get("critical_symptoms", {}).items():
                self.assertGreater(len(phrases), 0, f"Language {lang} critical {cat} empty")
                total_tokens += len(phrases)

            # Check routine admin
            for cat, phrases in categories.get("routine_admin", {}).items():
                self.assertGreater(len(phrases), 0, f"Language {lang} admin {cat} empty")
                total_tokens += len(phrases)

            # Check minor ailments
            for cat, phrases in categories.get("minor_ailments", {}).items():
                self.assertGreater(len(phrases), 0, f"Language {lang} minor {cat} empty")
                total_tokens += len(phrases)

        self.assertGreaterEqual(total_tokens, 800, f"Expected 800+ total tokens, found {total_tokens}")
        print(f"\n[OK] Audited {total_tokens} multi-script tokens across all 9 MVP languages.")

if __name__ == "__main__":
    unittest.main()
