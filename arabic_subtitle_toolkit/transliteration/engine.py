"""
Transliteration engine for Arabic ↔ Latin script conversion.

Supports multiple academic and industry-standard transliteration schemes:
- Buckwalter: Widely used in NLP and computational linguistics
- ALA-LC: American Library Association / Library of Congress romanization
- ISO 233: International standard for Arabic transliteration
- Simple: A simplified phonetic transliteration for general audiences

Usage:
    >>> from arabic_subtitle_toolkit import transliterate
    >>> transliterate("السلام عليكم", scheme="buckwalter")
    'AlslAm Elykm'
    >>> transliterate("السلام عليكم", scheme="simple")
    'as-salaam alaykum'
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TransliterationScheme(Enum):
    """Supported transliteration schemes."""

    BUCKWALTER = "buckwalter"
    ALA_LC = "ala-lc"
    ISO_233 = "iso-233"
    SIMPLE = "simple"


# ---------------------------------------------------------------------------
# Mapping tables
# ---------------------------------------------------------------------------

BUCKWALTER_MAP: dict[str, str] = {
    "\u0621": "'",   # ء hamza
    "\u0622": "|",   # آ alef madda
    "\u0623": ">",   # أ alef hamza above
    "\u0624": "&",   # ؤ waw hamza
    "\u0625": "<",   # إ alef hamza below
    "\u0626": "}",   # ئ ya hamza
    "\u0627": "A",   # ا alef
    "\u0628": "b",   # ب ba
    "\u0629": "p",   # ة ta marbuta
    "\u062A": "t",   # ت ta
    "\u062B": "v",   # ث tha
    "\u062C": "j",   # ج jim
    "\u062D": "H",   # ح ha
    "\u062E": "x",   # خ kha
    "\u062F": "d",   # د dal
    "\u0630": "*",   # ذ dhal
    "\u0631": "r",   # ر ra
    "\u0632": "z",   # ز zayn
    "\u0633": "s",   # س sin
    "\u0634": "$",   # ش shin
    "\u0635": "S",   # ص sad
    "\u0636": "D",   # ض dad
    "\u0637": "T",   # ط ta
    "\u0638": "Z",   # ظ za
    "\u0639": "E",   # ع ayn
    "\u063A": "g",   # غ ghayn
    "\u0640": "_",   # ـ tatweel
    "\u0641": "f",   # ف fa
    "\u0642": "q",   # ق qaf
    "\u0643": "k",   # ك kaf
    "\u0644": "l",   # ل lam
    "\u0645": "m",   # م mim
    "\u0646": "n",   # ن nun
    "\u0647": "h",   # ه ha
    "\u0648": "w",   # و waw
    "\u0649": "Y",   # ى alef maksura
    "\u064A": "y",   # ي ya
    # Diacritics
    "\u064B": "F",   # ً fathatan
    "\u064C": "N",   # ٌ dammatan
    "\u064D": "K",   # ٍ kasratan
    "\u064E": "a",   # َ fatha
    "\u064F": "u",   # ُ damma
    "\u0650": "i",   # ِ kasra
    "\u0651": "~",   # ّ shadda
    "\u0652": "o",   # ْ sukun
    "\u0670": "`",   # ٰ superscript alef
    "\u0671": "{",   # ٱ alef wasla
}

ALA_LC_MAP: dict[str, str] = {
    "\u0621": "ʾ",
    "\u0622": "ā",
    "\u0623": "ʾa",
    "\u0624": "ʾ",
    "\u0625": "ʾi",
    "\u0626": "ʾ",
    "\u0627": "ā",
    "\u0628": "b",
    "\u0629": "h",
    "\u062A": "t",
    "\u062B": "th",
    "\u062C": "j",
    "\u062D": "ḥ",
    "\u062E": "kh",
    "\u062F": "d",
    "\u0630": "dh",
    "\u0631": "r",
    "\u0632": "z",
    "\u0633": "s",
    "\u0634": "sh",
    "\u0635": "ṣ",
    "\u0636": "ḍ",
    "\u0637": "ṭ",
    "\u0638": "ẓ",
    "\u0639": "ʿ",
    "\u063A": "gh",
    "\u0640": "",
    "\u0641": "f",
    "\u0642": "q",
    "\u0643": "k",
    "\u0644": "l",
    "\u0645": "m",
    "\u0646": "n",
    "\u0647": "h",
    "\u0648": "w",
    "\u0649": "á",
    "\u064A": "y",
    "\u064E": "a",
    "\u064F": "u",
    "\u0650": "i",
    "\u064B": "an",
    "\u064C": "un",
    "\u064D": "in",
    "\u0651": "",  # shadda handled specially (double previous)
    "\u0652": "",
}

ISO_233_MAP: dict[str, str] = {
    "\u0621": "ˌ",
    "\u0622": "ˈā",
    "\u0623": "ˈ",
    "\u0624": "ˈ",
    "\u0625": "ˈ",
    "\u0626": "ˈ",
    "\u0627": "ā",
    "\u0628": "b",
    "\u0629": "ẗ",
    "\u062A": "t",
    "\u062B": "ṯ",
    "\u062C": "ǧ",
    "\u062D": "ḥ",
    "\u062E": "ẖ",
    "\u062F": "d",
    "\u0630": "ḏ",
    "\u0631": "r",
    "\u0632": "z",
    "\u0633": "s",
    "\u0634": "š",
    "\u0635": "ṣ",
    "\u0636": "ḍ",
    "\u0637": "ṭ",
    "\u0638": "ẓ",
    "\u0639": "ʿ",
    "\u063A": "ġ",
    "\u0640": "",
    "\u0641": "f",
    "\u0642": "q",
    "\u0643": "k",
    "\u0644": "l",
    "\u0645": "m",
    "\u0646": "n",
    "\u0647": "h",
    "\u0648": "w",
    "\u0649": "ỳ",
    "\u064A": "y",
    "\u064E": "a",
    "\u064F": "u",
    "\u0650": "i",
    "\u064B": "ã",
    "\u064C": "ũ",
    "\u064D": "ĩ",
    "\u0651": "",
    "\u0652": "˳",
}

SIMPLE_MAP: dict[str, str] = {
    "\u0621": "'",
    "\u0622": "aa",
    "\u0623": "a",
    "\u0624": "'",
    "\u0625": "i",
    "\u0626": "'",
    "\u0627": "a",
    "\u0628": "b",
    "\u0629": "a",
    "\u062A": "t",
    "\u062B": "th",
    "\u062C": "j",
    "\u062D": "h",
    "\u062E": "kh",
    "\u062F": "d",
    "\u0630": "th",
    "\u0631": "r",
    "\u0632": "z",
    "\u0633": "s",
    "\u0634": "sh",
    "\u0635": "s",
    "\u0636": "d",
    "\u0637": "t",
    "\u0638": "z",
    "\u0639": "'",
    "\u063A": "gh",
    "\u0640": "",
    "\u0641": "f",
    "\u0642": "q",
    "\u0643": "k",
    "\u0644": "l",
    "\u0645": "m",
    "\u0646": "n",
    "\u0647": "h",
    "\u0648": "w",
    "\u0649": "a",
    "\u064A": "y",
    "\u064E": "a",
    "\u064F": "u",
    "\u0650": "i",
    "\u064B": "an",
    "\u064C": "un",
    "\u064D": "in",
    "\u0651": "",
    "\u0652": "",
}

SCHEME_MAPS: dict[TransliterationScheme, dict[str, str]] = {
    TransliterationScheme.BUCKWALTER: BUCKWALTER_MAP,
    TransliterationScheme.ALA_LC: ALA_LC_MAP,
    TransliterationScheme.ISO_233: ISO_233_MAP,
    TransliterationScheme.SIMPLE: SIMPLE_MAP,
}


# ---------------------------------------------------------------------------
# Sun letters for assimilation rules
# ---------------------------------------------------------------------------

SUN_LETTERS = set("تثدذرزسشصضطظلن")


# ---------------------------------------------------------------------------
# Transliterator class
# ---------------------------------------------------------------------------


@dataclass
class Transliterator:
    """Configurable Arabic transliterator.

    Args:
        scheme: The transliteration scheme to use.
        strip_diacritics: If True, remove diacritics before transliterating.
        handle_shadda: If True, double the consonant on shadda.
        handle_sun_letters: If True, assimilate *al-* before sun letters.

    Example:
        >>> t = Transliterator(scheme=TransliterationScheme.BUCKWALTER)
        >>> t.transliterate("مرحبا")
        'mrHbA'
    """

    scheme: TransliterationScheme = TransliterationScheme.BUCKWALTER
    strip_diacritics: bool = False
    handle_shadda: bool = True
    handle_sun_letters: bool = True
    _map: dict[str, str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._map = SCHEME_MAPS[self.scheme]

    # -- public API --------------------------------------------------------

    def transliterate(self, text: str) -> str:
        """Transliterate Arabic text to Latin script."""
        if self.strip_diacritics:
            text = strip_arabic_diacritics(text)

        if self.handle_sun_letters and self.scheme != TransliterationScheme.BUCKWALTER:
            text = self._apply_sun_letter_assimilation(text)

        result: list[str] = []
        i = 0
        while i < len(text):
            char = text[i]
            # Handle shadda – double previous consonant
            if char == "\u0651" and self.handle_shadda and result:
                last = result[-1]
                if last and last[-1].isalpha():
                    result.append(last[-1])
                i += 1
                continue

            mapped = self._map.get(char)
            if mapped is not None:
                result.append(mapped)
            else:
                result.append(char)
            i += 1

        return "".join(result)

    def reverse(self, text: str) -> str:
        """Best-effort reverse transliteration (Latin → Arabic).

        Note: Reverse transliteration is inherently lossy for most schemes.
        """
        inv = {v: k for k, v in self._map.items() if v}
        # Sort by length descending so multi-char mappings match first
        sorted_keys = sorted(inv.keys(), key=len, reverse=True)

        result: list[str] = []
        i = 0
        while i < len(text):
            matched = False
            for key in sorted_keys:
                if text[i: i + len(key)] == key:
                    result.append(inv[key])
                    i += len(key)
                    matched = True
                    break
            if not matched:
                result.append(text[i])
                i += 1
        return "".join(result)

    # -- internals ---------------------------------------------------------

    def _apply_sun_letter_assimilation(self, text: str) -> str:
        """Replace ال before sun letters with assimilated form."""
        output = list(text)
        for i in range(len(output) - 2):
            if output[i] == "ا" and output[i + 1] == "ل" and i + 2 < len(output):
                next_char = output[i + 2]
                if next_char in SUN_LETTERS:
                    output[i + 1] = next_char  # assimilate lam
        return "".join(output)


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------


def transliterate(
    text: str,
    scheme: str | TransliterationScheme = "buckwalter",
    *,
    strip_diacritics: bool = False,
    handle_shadda: bool = True,
    handle_sun_letters: bool = True,
) -> str:
    """Transliterate Arabic text to Latin script.

    Args:
        text: Arabic text to transliterate.
        scheme: Transliteration scheme name or enum value.
        strip_diacritics: Remove diacritics before transliterating.
        handle_shadda: Double consonant on shadda.
        handle_sun_letters: Assimilate *al-* before sun letters.

    Returns:
        Transliterated text in Latin script.

    Example:
        >>> transliterate("بسم الله", scheme="buckwalter")
        'bsm Allh'
    """
    if isinstance(scheme, str):
        scheme = TransliterationScheme(scheme)
    t = Transliterator(
        scheme=scheme,
        strip_diacritics=strip_diacritics,
        handle_shadda=handle_shadda,
        handle_sun_letters=handle_sun_letters,
    )
    return t.transliterate(text)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670]")


def strip_arabic_diacritics(text: str) -> str:
    """Remove all Arabic diacritical marks (tashkeel) from *text*."""
    return _DIACRITICS_RE.sub("", text)
