"""
Example: Process Arabic subtitles for a YouTube video.

This script demonstrates a typical workflow for content creators
who need to process Arabic subtitles for multilingual distribution.
"""

from arabic_subtitle_toolkit import (
    transliterate,
    normalize_arabic,
    parse_subtitles,
    ArabicNormalizer,
    SubtitleFile,
    SubtitleEntry,
)
from arabic_subtitle_toolkit.subtitles.parser import Timestamp


def example_transliteration():
    """Show different transliteration schemes."""
    text = "بسم الله الرحمن الرحيم"
    print("=== Transliteration ===")
    print(f"Original: {text}")
    print(f"Buckwalter: {transliterate(text, scheme='buckwalter')}")
    print(f"ALA-LC:     {transliterate(text, scheme='ala-lc')}")
    print(f"ISO 233:    {transliterate(text, scheme='iso-233')}")
    print(f"Simple:     {transliterate(text, scheme='simple')}")
    print()


def example_normalization():
    """Show Arabic text normalization."""
    samples = [
        ("الْإِسْلَامُ", "With diacritics"),
        ("كتـــاب", "With tatweel"),
        ("إِبْرَاهِيم", "Alef variant"),
    ]
    print("=== Normalization ===")
    for text, desc in samples:
        normalized = normalize_arabic(text)
        print(f"{desc}: {text} → {normalized}")
    print()


def example_create_subtitles():
    """Create subtitle file programmatically."""
    print("=== Create Subtitles ===")
    entries = [
        SubtitleEntry(
            index=1,
            start=Timestamp(total_ms=1000),
            end=Timestamp(total_ms=4000),
            text="بسم الله الرحمن الرحيم",
        ),
        SubtitleEntry(
            index=2,
            start=Timestamp(total_ms=5000),
            end=Timestamp(total_ms=8000),
            text="In the name of God, the Most Gracious, the Most Merciful",
        ),
        SubtitleEntry(
            index=3,
            start=Timestamp(total_ms=9000),
            end=Timestamp(total_ms=12000),
            text="الحمد لله رب العالمين",
        ),
    ]

    subs = SubtitleFile(entries=entries, source_format="srt")
    print(f"Created {len(subs)} entries")

    # Add RTL markers
    subs.wrap_rtl()
    print("Added RTL markers")

    # Save as SRT
    subs.save("/tmp/example_output.srt")
    print("Saved: /tmp/example_output.srt")

    # Save as VTT
    subs.save("/tmp/example_output.vtt")
    print("Saved: /tmp/example_output.vtt")
    print()


if __name__ == "__main__":
    example_transliteration()
    example_normalization()
    example_create_subtitles()
    print("Done!")
