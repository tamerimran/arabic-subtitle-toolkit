"""
Arabic text normalization utilities.

Provides a configurable normalizer for common Arabic text inconsistencies:
    - Alef variants → bare Alef
    - Ta Marbuta ↔ Ha
    - Removing or preserving diacritics (tashkeel)
    - Removing tatweel (kashida)
    - Unicode normalization (NFC / NFKC)
    - Whitespace cleanup

Usage:
    >>> from arabic_subtitle_toolkit import normalize_arabic
    >>> normalize_arabic("إسْلاَمٌ")
    'اسلام'
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Character groups
# ---------------------------------------------------------------------------

# Alef variants
ALEF_VARIANTS = {
    "\u0622",  # آ  Alef Madda
    "\u0623",  # أ  Alef Hamza Above
    "\u0625",  # إ  Alef Hamza Below
    "\u0671",  # ٱ  Alef Wasla
    "\u0672",  #    Alef Wavy Hamza Above
    "\u0673",  #    Alef Wavy Hamza Below
}

ALEF_BARE = "\u0627"  # ا

# Diacritics (tashkeel) range
_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670]")

# Tatweel / Kashida
TATWEEL = "\u0640"

# Ya variants
YA_VARIANTS = {"\u0649"}  # ى  Alef Maksura
YA_STANDARD = "\u064A"  # ي

# Waw Hamza
WAW_HAMZA = "\u0624"  # ؤ

# Ha / Ta Marbuta
TA_MARBUTA = "\u0629"  # ة
HA = "\u0647"  # ه

# Hamza variants
HAMZA_VARIANTS = {"\u0621", "\u0623", "\u0624", "\u0625", "\u0626"}
HAMZA_BARE = "\u0621"  # ء


# ---------------------------------------------------------------------------
# Normalizer class
# ---------------------------------------------------------------------------


@dataclass
class ArabicNormalizer:
    """Configurable Arabic text normalizer.

    All flags default to ``True`` for maximum normalization; set individual
    flags to ``False`` to preserve specific features.

    Args:
        normalize_alef: Map Alef variants to bare Alef.
        normalize_ya: Map Alef Maksura to Ya.
        normalize_ta_marbuta: Map Ta Marbuta to Ha.
        remove_diacritics: Strip all diacritical marks.
        remove_tatweel: Strip kashida/tatweel characters.
        remove_non_arabic: Strip non-Arabic, non-space characters.
        strip_whitespace: Collapse multiple spaces and trim.
        unicode_normalize: Apply NFC Unicode normalization.

    Example:
        >>> n = ArabicNormalizer(remove_diacritics=True)
        >>> n.normalize("بِسْمِ اللَّهِ")
        'بسم الله'
    """

    normalize_alef: bool = True
    normalize_ya: bool = True
    normalize_ta_marbuta: bool = False  # off by default – changes meaning
    remove_diacritics: bool = True
    remove_tatweel: bool = True
    remove_non_arabic: bool = False
    strip_whitespace: bool = True
    unicode_normalize: bool = True

    def normalize(self, text: str) -> str:
        """Apply all enabled normalization steps to *text*."""
        if self.unicode_normalize:
            text = unicodedata.normalize("NFC", text)

        if self.remove_diacritics:
            text = _DIACRITICS_RE.sub("", text)

        if self.remove_tatweel:
            text = text.replace(TATWEEL, "")

        if self.normalize_alef:
            for v in ALEF_VARIANTS:
                text = text.replace(v, ALEF_BARE)

        if self.normalize_ya:
            for v in YA_VARIANTS:
                text = text.replace(v, YA_STANDARD)

        if self.normalize_ta_marbuta:
            text = text.replace(TA_MARBUTA, HA)

        if self.remove_non_arabic:
            text = re.sub(r"[^\u0600-\u06FF\u0750-\u077F\s]", "", text)

        if self.strip_whitespace:
            text = re.sub(r"\s+", " ", text).strip()

        return text


# ---------------------------------------------------------------------------
# Default normalizer instance and convenience function
# ---------------------------------------------------------------------------

_DEFAULT_NORMALIZER = ArabicNormalizer()


def normalize_arabic(
    text: str,
    *,
    normalize_alef: bool = True,
    normalize_ya: bool = True,
    normalize_ta_marbuta: bool = False,
    remove_diacritics: bool = True,
    remove_tatweel: bool = True,
    remove_non_arabic: bool = False,
    strip_whitespace: bool = True,
    unicode_normalize: bool = True,
) -> str:
    """Normalize Arabic text with configurable options.

    This is a convenience wrapper around :class:`ArabicNormalizer`.

    Example:
        >>> normalize_arabic("الْإِسْلَام")
        'الاسلام'
    """
    n = ArabicNormalizer(
        normalize_alef=normalize_alef,
        normalize_ya=normalize_ya,
        normalize_ta_marbuta=normalize_ta_marbuta,
        remove_diacritics=remove_diacritics,
        remove_tatweel=remove_tatweel,
        remove_non_arabic=remove_non_arabic,
        strip_whitespace=strip_whitespace,
        unicode_normalize=unicode_normalize,
    )
    return n.normalize(text)
