"""
arabic.py - display Arabic text correctly, when the computer can't do it alone.

Arabic is written from RIGHT to LEFT, and the letters change shape depending
on their position in a word (isolated, at the end, at the start, in the middle).
Windows and Mac do this automatically. On Linux, tkinter can't, so this file:
    1) "shapes" each word: chooses the right form of each letter
    2) puts the words in visual order (right to left), keeping English words
       and numbers (like "Synergix" or "10:25") from left to right
    3) cuts long texts into lines (because we draw the lines ourselves)
"""

import re

# letter: (isolated, final, initial, medial) - None = this form doesn't exist
FORMS = {
    "ء": ("ﺀ", None, None, None),
    "آ": ("ﺁ", "ﺂ", None, None),
    "أ": ("ﺃ", "ﺄ", None, None),
    "ؤ": ("ﺅ", "ﺆ", None, None),
    "إ": ("ﺇ", "ﺈ", None, None),
    "ئ": ("ﺉ", "ﺊ", "ﺋ", "ﺌ"),
    "ا": ("ﺍ", "ﺎ", None, None),
    "ب": ("ﺏ", "ﺐ", "ﺑ", "ﺒ"),
    "ة": ("ﺓ", "ﺔ", None, None),
    "ت": ("ﺕ", "ﺖ", "ﺗ", "ﺘ"),
    "ث": ("ﺙ", "ﺚ", "ﺛ", "ﺜ"),
    "ج": ("ﺝ", "ﺞ", "ﺟ", "ﺠ"),
    "ح": ("ﺡ", "ﺢ", "ﺣ", "ﺤ"),
    "خ": ("ﺥ", "ﺦ", "ﺧ", "ﺨ"),
    "د": ("ﺩ", "ﺪ", None, None),
    "ذ": ("ﺫ", "ﺬ", None, None),
    "ر": ("ﺭ", "ﺮ", None, None),
    "ز": ("ﺯ", "ﺰ", None, None),
    "س": ("ﺱ", "ﺲ", "ﺳ", "ﺴ"),
    "ش": ("ﺵ", "ﺶ", "ﺷ", "ﺸ"),
    "ص": ("ﺹ", "ﺺ", "ﺻ", "ﺼ"),
    "ض": ("ﺽ", "ﺾ", "ﺿ", "ﻀ"),
    "ط": ("ﻁ", "ﻂ", "ﻃ", "ﻄ"),
    "ظ": ("ﻅ", "ﻆ", "ﻇ", "ﻈ"),
    "ع": ("ﻉ", "ﻊ", "ﻋ", "ﻌ"),
    "غ": ("ﻍ", "ﻎ", "ﻏ", "ﻐ"),
    "ـ": ("ـ", "ـ", "ـ", "ـ"),      # tatweel (a line)
    "ف": ("ﻑ", "ﻒ", "ﻓ", "ﻔ"),
    "ق": ("ﻕ", "ﻖ", "ﻗ", "ﻘ"),
    "ك": ("ﻙ", "ﻚ", "ﻛ", "ﻜ"),
    "ل": ("ﻝ", "ﻞ", "ﻟ", "ﻠ"),
    "م": ("ﻡ", "ﻢ", "ﻣ", "ﻤ"),
    "ن": ("ﻥ", "ﻦ", "ﻧ", "ﻨ"),
    "ه": ("ﻩ", "ﻪ", "ﻫ", "ﻬ"),
    "و": ("ﻭ", "ﻮ", None, None),
    "ى": ("ﻯ", "ﻰ", None, None),
    "ي": ("ﻱ", "ﻲ", "ﻳ", "ﻴ"),
}
# lam + alef make one special letter: (isolated, final)
LAM_ALEF = {"آ": ("ﻵ", "ﻶ"), "أ": ("ﻷ", "ﻸ"),
            "إ": ("ﻹ", "ﻺ"), "ا": ("ﻻ", "ﻼ")}
LAM = "ل"
MIRROR = {"(": ")", ")": "(", "[": "]", "]": "[", "«": "»", "»": "«", "<": ">", ">": "<"}


def is_arabic(ch):
    return "؀" <= ch <= "ۿ" or "ﹰ" <= ch <= "﻿"


def has_arabic(text):
    return any(is_arabic(ch) for ch in text)


def shape(word):
    """Choose the right form of each Arabic letter (the word stays in logical order)."""
    out = []
    prev_joins = False                 # can the previous letter connect to this one?
    i = 0
    while i < len(word):
        ch = word[i]
        nxt = word[i + 1] if i + 1 < len(word) else ""
        if ch == LAM and nxt in LAM_ALEF:                      # lam-alef ligature
            out.append(LAM_ALEF[nxt][1 if prev_joins else 0])
            prev_joins = False
            i += 2
            continue
        forms = FORMS.get(ch)
        if forms is None:                                      # not an Arabic letter
            out.append(ch)
            prev_joins = False
            i += 1
            continue
        join_before = prev_joins and forms[1] is not None
        join_after = forms[2] is not None and nxt in FORMS and FORMS[nxt][1] is not None
        if join_before and join_after:
            out.append(forms[3])
        elif join_before:
            out.append(forms[1])
        elif join_after:
            out.append(forms[2])
        else:
            out.append(forms[0])
        prev_joins = forms[2] is not None
        i += 1
    return "".join(out)


def _split_word(word):
    """'(Mayeul),' -> ('(', 'Mayeul', '),')   (Arabic commas count as punctuation)"""
    start, end = 0, len(word)
    while start < end and not word[start].isalnum():
        start += 1
    while end > start and not word[end - 1].isalnum():
        end -= 1
    return word[:start], word[start:end], word[end:]


def _mirror(text):
    return "".join(MIRROR.get(ch, ch) for ch in text)


def _reverse_arabic(word):
    """Reverse an Arabic word for display, but keep numbers like '12' readable."""
    parts = re.findall(r"[0-9]+|[^0-9]+", shape(word))
    return "".join(p if p.isdigit() else _mirror(p[::-1]) for p in reversed(parts))


def visual_line(line):
    """Put one line in visual order: right to left, English words left to right."""
    runs = []                                  # [is_english, [words]]
    for word in line.split(" "):
        core = _split_word(word)[1]
        english = bool(core) and not has_arabic(core)
        if english and runs and runs[-1][0] and not _split_word(runs[-1][1][-1])[2]:
            runs[-1][1].append(word)           # English words stay together, in order
        else:
            runs.append([english, [word]])
    out = []
    for english, words in reversed(runs):
        if english:
            lead, core, trail = _split_word(" ".join(words))
            out.append(_mirror(trail[::-1]) + core + _mirror(lead[::-1]))
        else:
            out.append(_reverse_arabic(words[0]))
    return " ".join(out)


def wrap(paragraph, measure, width):
    """Cut a paragraph into lines no wider than `width` pixels."""
    lines, current = [], ""
    for word in paragraph.split(" "):
        test = f"{current} {word}" if current else word
        if current and measure(shape(test)) > width:
            lines.append(current)
            current = word
        else:
            current = test
    return lines + [current]


def visual_text(text, measure=None, width=None):
    """The whole text, ready to draw: shaped, cut into lines, right to left."""
    if not has_arabic(text):
        return text
    lines = []
    for paragraph in text.split("\n"):
        parts = wrap(paragraph, measure, width) if (measure and width) else [paragraph]
        lines += [visual_line(part) for part in parts]
    return "\n".join(lines)
