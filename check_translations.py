"""
check_translations.py - is every English text translated?

Run:  python check_translations.py

It collects every text of the game:
    - the story (story.py): dialogues, choices, notes, endings, trophies...
    - every t("...") in the code (game.py, terminal.py, engine.py)
and checks that lang_fr.py, lang_de.py and lang_ar.py have a translation.
"""

import ast
from pathlib import Path

import story
from i18n import TRANSLATIONS

HERE = Path(__file__).resolve().parent


def story_texts():
    texts = [story.DEFAULT_NAME, story.TIMEOUT_LINE[1], story.TOO_SLOW_NOTE]
    for character in story.CHARACTERS.values():
        texts += [character["name"], character["role"]]
    for part in list(story.SCENES.values()) + list(story.ENDINGS.values()):
        texts += [part["location"], part["time"], part.get("title", "")]
        texts += [part.get("question") or ""]
        texts += [text for _, text in part["lines"]]
        for choice in part.get("choices", []):
            texts += [choice["label"], choice.get("note", "")]
            texts += [text for _, text in choice["reaction"]]
    texts += [track["name"] for track in story.TRACKS.values()]
    texts += list(story.NOTEBOOK_VERDICTS.values()) + list(story.MENU_QUOTES)
    for title, description in story.ACHIEVEMENTS.values():
        texts += [title, description]
    # times like "10:25" don't need a translation, but "MONDAY" does
    return [x for x in texts if x and any(ch.isalpha() for ch in x)]


def code_texts():
    """Find every t("...") in the Python files."""
    texts = []
    for name in ("game.py", "terminal.py", "engine.py"):
        tree = ast.parse((HERE / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "t"
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                texts.append(node.args[0].value)
    return texts


def all_texts():
    """Every English text, in order, without duplicates."""
    return list(dict.fromkeys(story_texts() + code_texts()))


if __name__ == "__main__":
    texts = all_texts()
    print(f"{len(texts)} English texts in the game.")
    for code, table in TRANSLATIONS.items():
        missing = [x for x in texts if x not in table]
        unused = [x for x in table if x not in texts]
        print(f"  {code}: {len(texts) - len(missing)} translated, {len(missing)} missing, "
              f"{len(unused)} not used")
        for x in missing[:10]:
            print(f"      missing: {x[:70]!r}")
        for x in unused[:10]:
            print(f"      not used: {x[:70]!r}")
