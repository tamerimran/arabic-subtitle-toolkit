"""
Arabic Subtitle Toolkit (AST)
=============================

A comprehensive Python toolkit for Arabic subtitle processing,
transliteration, and text normalization.

Features:
    - Arabic ↔ Latin transliteration (Buckwalter, ALA-LC, ISO 233)
    - Subtitle file parsing and generation (SRT, VTT, ASS/SSA)
    - Arabic text normalization and diacritics handling
    - RTL-aware subtitle formatting
    - Batch processing for multilingual subtitle workflows

Example:
    >>> from arabic_subtitle_toolkit import transliterate, parse_subtitles
    >>> transliterate("بسم الله الرحمن الرحيم", scheme="ala-lc")
    'bismi allāhi al-raḥmāni al-raḥīmi'
    >>> subs = parse_subtitles("my_video.srt")
    >>> subs.normalize().save("my_video_clean.srt")
"""

__version__ = "0.1.0"
__author__ = "Tamer Imran"
__license__ = "MIT"

from arabic_subtitle_toolkit.transliteration.engine import (
    transliterate,
    Transliterator,
    TransliterationScheme,
)
from arabic_subtitle_toolkit.subtitles.parser import (
    parse_subtitles,
    SubtitleFile,
    SubtitleEntry,
)
from arabic_subtitle_toolkit.normalization.normalizer import (
    normalize_arabic,
    ArabicNormalizer,
)

__all__ = [
    "transliterate",
    "Transliterator",
    "TransliterationScheme",
    "parse_subtitles",
    "SubtitleFile",
    "SubtitleEntry",
    "normalize_arabic",
    "ArabicNormalizer",
]
