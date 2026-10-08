"""
i18n.py - TRANSLATIONS ("i18n" = "internationalisation": i + 18 letters + n).

The game is written in English. For the other languages, each English
sentence has a translation in a dictionary:

    lang_fr.py   French    TEXTS = {"English sentence": "Phrase en français", ...}
    lang_de.py   German
    lang_ar.py   Arabic

t("Some English text") returns the text in the current language. If a
translation is missing, the English text is shown (the game never crashes).
"""

import arabic
import lang_ar
import lang_de
import lang_fr

LANGUAGES = {"en": "English", "fr": "Français", "de": "Deutsch", "ar": "العربية"}
TRANSLATIONS = {"fr": lang_fr.TEXTS, "de": lang_de.TEXTS, "ar": lang_ar.TEXTS}
RIGHT_TO_LEFT = {"ar"}

current = "en"
manual_arabic = False     # True on Linux: we must draw Arabic letters ourselves


def set_language(code):
    global current
    current = code if code in LANGUAGES else "en"


def t(text):
    """Translate an English text into the current language."""
    if current == "en":
        return text
    return TRANSLATIONS[current].get(text, text)


def is_rtl():
    """Is the current language written from right to left?"""
    return current in RIGHT_TO_LEFT


def vis(text, measure=None, width=None):
    """The text ready to draw on screen (only changes Arabic on Linux)."""
    if manual_arabic and arabic.has_arabic(text):
        return arabic.visual_text(text, measure, width)
    return text
