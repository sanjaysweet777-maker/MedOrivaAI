# blended_engine.py
import re
from datetime import datetime, timezone
from blended_config import EXPANDED_LEXICON

class BlendedLanguageProcessor:
    def __init__(self):
        self.lexicon = EXPANDED_LEXICON

    def _get_lang_key(self, lang_code: str) -> str:
        """Normalizes any incoming language string (e.g. 'Tamil', 'ta-IN', 'ta') to the 2-letter key."""
        if not lang_code:
            return "ta"
        clean = str(lang_code).strip().lower().split('-')[0].split('_')[0]
        name_map = {
            "tamil": "ta", "hindi": "hi", "malayalam": "ml", "polish": "pl",
            "arabic": "ar", "urdu": "ur", "bengali": "bn", "somali": "so", "romanian": "ro"
        }
        return name_map.get(clean, clean)

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def detect_negation(self, lang_code: str, norm_text: str) -> bool:
        key = self._get_lang_key(lang_code)
        tokens = self.lexicon.get(key, {}).get("negation", [])
        words = norm_text.split()
        for token in tokens:
            if " " in token:
                # Multi-word negation phrase check
                if re.search(r'\b' + re.escape(token) + r'\b', norm_text):
                    return True
            else:
                # Single-word exact token match
                if token in words:
                    return True
        return False

    def _scan_category(self, section_dict: dict, norm_text: str):
        """Scans a section dictionary using word boundaries, prioritising longer phrases first."""
        all_candidates = []
        for cat, phrases in section_dict.items():
            for p in phrases:
                all_candidates.append((cat, p))
        
        # Sort by phrase length descending (longest match wins)
        all_candidates.sort(key=lambda x: len(x[1]), reverse=True)

        for cat, p in all_candidates:
            if re.search(r'\b' + re.escape(p) + r'\b', norm_text):
                return cat, p
        return None, None

    def scan_critical(self, lang_code: str, norm_text: str):
        key = self._get_lang_key(lang_code)
        crit_dict = self.lexicon.get(key, {}).get("critical_symptoms", {})
        return self._scan_category(crit_dict, norm_text)

    def scan_routine_admin(self, lang_code: str, norm_text: str):
        key = self._get_lang_key(lang_code)
        admin_dict = self.lexicon.get(key, {}).get("routine_admin", {})
        return self._scan_category(admin_dict, norm_text)

    def scan_minor_ailments(self, lang_code: str, norm_text: str):
        key = self._get_lang_key(lang_code)
        minor_dict = self.lexicon.get(key, {}).get("minor_ailments", {})
        return self._scan_category(minor_dict, norm_text)

    def process_intake(self, lang_code: str, raw_text: str) -> dict:
        key = self._get_lang_key(lang_code)
        norm = self.normalize(raw_text)
        has_neg = self.detect_negation(key, norm)
        crit_cat, _ = self.scan_critical(key, norm)
        admin_cat, _ = self.scan_routine_admin(key, norm)
        minor_cat, _ = self.scan_minor_ailments(key, norm)

        # Standard ISO UTC timestamp
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        response = {
            "timestamp": ts,
            "language_code": key,
            "raw_input": raw_text,
            "normalized_input": norm,
            "communication_cue": False,
            "meaning_check": False,
            "extracted_meaning": "",
            "cue_message": None,
            "clipboard_summary": ""
        }

        # Priority 1: selected symptom-related wording for neutral staff review
        if crit_cat:
            cat_name = crit_cat.replace("_", " ").title()
            response["communication_cue"] = True
            if has_neg:
                response["meaning_check"] = True
                response["extracted_meaning"] = f"Negative wording detected with {cat_name} wording"
                response["cue_message"] = (
                    "Negative wording detected — confirm that the negative meaning "
                    "has been preserved."
                )
            else:
                response["extracted_meaning"] = f"Symptom-related wording present: {cat_name}"
                response["cue_message"] = (
                    "Communication cue: symptom-related information present. "
                    "Confirm meaning with the patient and apply the practice's normal staff-led process."
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

        # Produce a temporary staff-review output. This is not an EHR integration,
        # and it must not claim that a patient confirmation has occurred.
        cue_tag = "COMMUNICATION CUE — STAFF REVIEW" if response["communication_cue"] else "ROUTINE COMMUNICATION"
        neg_tag = "NEGATIVE WORDING DETECTED — CONFIRMATION REQUIRED" if has_neg else "NO NEGATION DETECTED"

        response["clipboard_summary"] = (
            f"[MedOriva Temporary Staff Review]\n"
            f"Language: {key.upper()} (Colloquial QWERTY) | Time: {response['timestamp']}\n"
            f"Administrative Interpretation: {response['extracted_meaning']}\n"
            f"Review state: {cue_tag} | Negation state: {neg_tag}\n"
            f"Confirmation status: Not recorded by this processing step\n"
            f"Note: Staff must verify meaning and record only what local practice policy requires."
        )

        return response
