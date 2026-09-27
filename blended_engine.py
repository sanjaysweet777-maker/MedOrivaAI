# blended_engine.py
import re
from datetime import datetime
from blended_config import EXPANDED_LEXICON

class BlendedLanguageProcessor:
    def __init__(self):
        self.lexicon = EXPANDED_LEXICON

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def detect_negation(self, lang_code: str, norm_text: str) -> bool:
        tokens = self.lexicon.get(lang_code, {}).get("negation", [])
        words = norm_text.split()
        for token in tokens:
            if " " in token:
                if token in norm_text:
                    return True
            else:
                if token in words:
                    return True
        return False

    def scan_critical(self, lang_code: str, norm_text: str):
        crit_dict = self.lexicon.get(lang_code, {}).get("critical_symptoms", {})
        for cat, phrases in crit_dict.items():
            for p in phrases:
                if p in norm_text:
                    return cat, p
        return None, None

    def scan_routine_admin(self, lang_code: str, norm_text: str):
        admin_dict = self.lexicon.get(lang_code, {}).get("routine_admin", {})
        for cat, phrases in admin_dict.items():
            for p in phrases:
                if p in norm_text:
                    return cat, p
        return None, None

    def scan_minor_ailments(self, lang_code: str, norm_text: str):
        minor_dict = self.lexicon.get(lang_code, {}).get("minor_ailments", {})
        for cat, phrases in minor_dict.items():
            for p in phrases:
                if p in norm_text:
                    return cat, p
        return None, None

    def process_intake(self, lang_code: str, raw_text: str) -> dict:
        norm = self.normalize(raw_text)
        has_neg = self.detect_negation(lang_code, norm)
        crit_cat, _ = self.scan_critical(lang_code, norm)
        admin_cat, _ = self.scan_routine_admin(lang_code, norm)
        minor_cat, _ = self.scan_minor_ailments(lang_code, norm)

        response = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "language_code": lang_code,
            "raw_input": raw_text,
            "normalized_input": norm,
            "communication_cue": False,
            "meaning_check": False,
            "extracted_meaning": "",
            "cue_message": None,
            "clipboard_summary": ""
        }

        # Priority 1: Critical Symptom Trigger
        if crit_cat:
            cat_name = crit_cat.replace("_", " ").title()
            response["communication_cue"] = True
            if has_neg:
                response["meaning_check"] = True
                response["extracted_meaning"] = f"Patient indicates NO {cat_name} (Negated report for staff review)"
                response["cue_message"] = (
                    "Negative wording detected alongside symptom terms. "
                    "Confirm with patient that negation was intended and preserved."
                )
            else:
                response["extracted_meaning"] = f"Patient reports potential {cat_name}"
                response["cue_message"] = (
                    "Communication cue: symptom-related information present. "
                    "Confirm meaning directly with patient. Follow standard practice urgent care protocols."
                )

        # Priority 2: Routine Administrative Intake (Clean by default)
        elif admin_cat:
            cat_name = admin_cat.replace("_", " ").title()
            neg_note = " [Negated / Cancelled]" if has_neg else ""
            response["extracted_meaning"] = f"Routine Intake: {cat_name}{neg_note}"

        # Priority 3: Routine Minor Ailment (Clean by default)
        elif minor_cat:
            cat_name = minor_cat.replace("_", " ").title()
            neg_note = " [Not present]" if has_neg else ""
            response["extracted_meaning"] = f"Routine Minor Ailment: {cat_name}{neg_note}"

        # Priority 4: General Translation Fallback
        else:
            response["extracted_meaning"] = raw_text

        # Format Note for EMIS Web / SystmOne One-Click Clipboard Export
        status_tag = "CRITICAL CUE FLAGGED" if response["communication_cue"] else "ROUTINE DIRECT"
        neg_tag = "NEGATION CONFIRMED" if has_neg else "AFFIRMATIVE"

        response["clipboard_summary"] = (
            f"[MedOriva Administrative Intake Note]\n"
            f"Language: {lang_code.upper()} (Colloquial QWERTY) | Time: {response['timestamp']}\n"
            f"Patient Input: \"{raw_text}\"\n"
            f"Administrative Interpretation: {response['extracted_meaning']}\n"
            f"Safety Protocol: {status_tag} | Negation State: {neg_tag}\n"
            f"Note: Bounded administrative intake only. Clinical consultations require qualified interpreters."
        )

        return response
