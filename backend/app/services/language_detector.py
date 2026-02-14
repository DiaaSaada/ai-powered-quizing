"""
Language Detection Service
Detects language from topic text and provides language names for prompts.
"""
from typing import Optional, Tuple
from lingua import Language, LanguageDetectorBuilder


# Supported languages with their prompt names
LANGUAGE_NAMES = {
    "ar": "Arabic",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
    "hi": "Hindi",
    "tr": "Turkish",
    "nl": "Dutch",
    "pl": "Polish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "he": "Hebrew",
    "fa": "Persian",
}

# Lingua Language to ISO 639-1 mapping
LINGUA_TO_ISO = {
    Language.ARABIC: "ar",
    Language.ENGLISH: "en",
    Language.SPANISH: "es",
    Language.FRENCH: "fr",
    Language.GERMAN: "de",
    Language.CHINESE: "zh",
    Language.JAPANESE: "ja",
    Language.KOREAN: "ko",
    Language.PORTUGUESE: "pt",
    Language.RUSSIAN: "ru",
    Language.ITALIAN: "it",
    Language.HINDI: "hi",
    Language.TURKISH: "tr",
    Language.DUTCH: "nl",
    Language.POLISH: "pl",
    Language.VIETNAMESE: "vi",
    Language.THAI: "th",
    Language.INDONESIAN: "id",
    Language.HEBREW: "he",
    Language.PERSIAN: "fa",
}


class LanguageDetector:
    """Detects language from text input."""

    def __init__(self):
        # Build detector for common languages
        self.detector = LanguageDetectorBuilder.from_languages(
            Language.ARABIC,
            Language.ENGLISH,
            Language.SPANISH,
            Language.FRENCH,
            Language.GERMAN,
            Language.CHINESE,
            Language.JAPANESE,
            Language.KOREAN,
            Language.PORTUGUESE,
            Language.RUSSIAN,
            Language.ITALIAN,
            Language.HINDI,
            Language.TURKISH,
            Language.DUTCH,
            Language.POLISH,
            Language.VIETNAMESE,
            Language.THAI,
            Language.INDONESIAN,
            Language.HEBREW,
            Language.PERSIAN,
        ).build()

    def detect(self, text: str) -> Tuple[str, str, float]:
        """
        Detect language from text.

        Args:
            text: Input text (topic, title, etc.)

        Returns:
            Tuple of (iso_code, language_name, confidence)
            Defaults to ("en", "English", 1.0) if detection fails
        """
        if not text or len(text.strip()) < 2:
            return ("en", "English", 1.0)

        try:
            result = self.detector.detect_language_of(text)
            if result and result in LINGUA_TO_ISO:
                iso_code = LINGUA_TO_ISO[result]
                lang_name = LANGUAGE_NAMES.get(iso_code, "English")
                confidence = self.detector.compute_language_confidence(text, result)
                return (iso_code, lang_name, confidence)
        except Exception:
            pass

        return ("en", "English", 1.0)

    def get_language_name(self, iso_code: str) -> str:
        """Get display name for ISO language code."""
        return LANGUAGE_NAMES.get(iso_code, "English")


# Singleton instance
_detector_instance: Optional[LanguageDetector] = None


def get_language_detector() -> LanguageDetector:
    """Get or create the LanguageDetector singleton."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = LanguageDetector()
    return _detector_instance
