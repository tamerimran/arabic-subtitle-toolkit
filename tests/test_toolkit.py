"""Tests for arabic_subtitle_toolkit."""

import tempfile
from pathlib import Path

import pytest

from arabic_subtitle_toolkit import (
    transliterate,
    Transliterator,
    TransliterationScheme,
    normalize_arabic,
    ArabicNormalizer,
    parse_subtitles,
    SubtitleFile,
    SubtitleEntry,
)
from arabic_subtitle_toolkit.subtitles.parser import Timestamp


# ======================================================================
# Transliteration tests
# ======================================================================


class TestTransliterate:
    """Tests for the transliteration module."""

    def test_buckwalter_basic(self):
        result = transliterate("بسم", scheme="buckwalter")
        assert result == "bsm"

    def test_buckwalter_full_phrase(self):
        result = transliterate("بسم الله", scheme="buckwalter")
        assert "bsm" in result
        assert "Allh" in result

    def test_ala_lc_scheme(self):
        result = transliterate("كتاب", scheme="ala-lc")
        assert result == "ktāb"

    def test_simple_scheme(self):
        result = transliterate("محمد", scheme="simple")
        assert "m" in result

    def test_iso_233_scheme(self):
        result = transliterate("عرب", scheme="iso-233")
        assert "ʿ" in result

    def test_preserves_non_arabic(self):
        result = transliterate("Hello بسم World", scheme="buckwalter")
        assert "Hello" in result
        assert "World" in result

    def test_empty_string(self):
        assert transliterate("") == ""

    def test_strip_diacritics(self):
        result = transliterate("بِسْمِ", scheme="buckwalter", strip_diacritics=True)
        assert result == "bsm"

    def test_transliterator_class(self):
        t = Transliterator(scheme=TransliterationScheme.BUCKWALTER)
        result = t.transliterate("كتب")
        assert result == "ktb"

    def test_reverse_transliteration(self):
        t = Transliterator(scheme=TransliterationScheme.BUCKWALTER)
        arabic = "كتب"
        latin = t.transliterate(arabic)
        reversed_back = t.reverse(latin)
        assert reversed_back == arabic


# ======================================================================
# Normalization tests
# ======================================================================


class TestNormalization:
    """Tests for the normalization module."""

    def test_remove_diacritics(self):
        result = normalize_arabic("بِسْمِ اللَّهِ")
        assert "ِ" not in result
        assert "ْ" not in result

    def test_normalize_alef(self):
        result = normalize_arabic("إسلام")
        assert result == "اسلام"

    def test_normalize_alef_madda(self):
        result = normalize_arabic("آمين")
        assert result.startswith("ا")

    def test_remove_tatweel(self):
        result = normalize_arabic("كتـــاب")
        assert "ـ" not in result
        assert result == "كتاب"

    def test_normalize_ya(self):
        result = normalize_arabic("على")
        assert result == "علي"

    def test_preserve_ta_marbuta_by_default(self):
        result = normalize_arabic("مدرسة")
        assert "ة" in result

    def test_normalize_ta_marbuta(self):
        result = normalize_arabic("مدرسة", normalize_ta_marbuta=True)
        assert "ة" not in result

    def test_strip_whitespace(self):
        result = normalize_arabic("كلمة   طويلة    جدا")
        assert "   " not in result

    def test_empty_string(self):
        assert normalize_arabic("") == ""

    def test_normalizer_class(self):
        n = ArabicNormalizer(remove_diacritics=True, normalize_alef=False)
        result = n.normalize("إِسْلَام")
        assert "إ" in result  # alef not normalized


# ======================================================================
# Subtitle parsing tests
# ======================================================================


class TestTimestamp:
    """Tests for the Timestamp class."""

    def test_from_srt(self):
        ts = Timestamp.from_srt("01:23:45,678")
        assert ts.total_ms == 1 * 3_600_000 + 23 * 60_000 + 45 * 1_000 + 678

    def test_from_vtt(self):
        ts = Timestamp.from_vtt("01:23:45.678")
        assert ts.total_ms == 1 * 3_600_000 + 23 * 60_000 + 45 * 1_000 + 678

    def test_to_srt(self):
        ts = Timestamp(total_ms=5025678)
        assert ts.to_srt() == "01:23:45,678"

    def test_to_vtt(self):
        ts = Timestamp(total_ms=5025678)
        assert ts.to_vtt() == "01:23:45.678"

    def test_shift_positive(self):
        ts = Timestamp(total_ms=1000)
        shifted = ts.shift(500)
        assert shifted.total_ms == 1500

    def test_shift_negative_clamp(self):
        ts = Timestamp(total_ms=100)
        shifted = ts.shift(-500)
        assert shifted.total_ms == 0


class TestSubtitleParsing:
    """Tests for SRT and VTT parsing."""

    SAMPLE_SRT = (
        "1\n"
        "00:00:01,000 --> 00:00:04,000\n"
        "بسم الله الرحمن الرحيم\n"
        "\n"
        "2\n"
        "00:00:05,000 --> 00:00:08,000\n"
        "In the name of God\n"
    )

    SAMPLE_VTT = (
        "WEBVTT\n"
        "\n"
        "00:00:01.000 --> 00:00:04.000\n"
        "بسم الله الرحمن الرحيم\n"
        "\n"
        "00:00:05.000 --> 00:00:08.000\n"
        "In the name of God\n"
    )

    def _write_tmp(self, content: str, suffix: str) -> Path:
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, delete=False, encoding="utf-8"
        )
        f.write(content)
        f.close()
        return Path(f.name)

    def test_parse_srt(self):
        path = self._write_tmp(self.SAMPLE_SRT, ".srt")
        subs = parse_subtitles(path)
        assert len(subs) == 2
        assert subs[0].contains_arabic()
        assert not subs[1].contains_arabic()

    def test_parse_vtt(self):
        path = self._write_tmp(self.SAMPLE_VTT, ".vtt")
        subs = parse_subtitles(path)
        assert len(subs) == 2

    def test_shift(self):
        path = self._write_tmp(self.SAMPLE_SRT, ".srt")
        subs = parse_subtitles(path)
        subs.shift(1000)
        assert subs[0].start.total_ms == 2000

    def test_filter_arabic(self):
        path = self._write_tmp(self.SAMPLE_SRT, ".srt")
        subs = parse_subtitles(path)
        arabic_only = subs.filter_arabic()
        assert len(arabic_only) == 1

    def test_save_srt(self):
        path = self._write_tmp(self.SAMPLE_SRT, ".srt")
        subs = parse_subtitles(path)
        out = self._write_tmp("", ".srt")
        subs.save(out)
        reloaded = parse_subtitles(out)
        assert len(reloaded) == 2

    def test_save_vtt(self):
        path = self._write_tmp(self.SAMPLE_SRT, ".srt")
        subs = parse_subtitles(path)
        out = self._write_tmp("", ".vtt")
        subs.save(out, fmt="vtt")
        content = out.read_text()
        assert "WEBVTT" in content

    def test_wrap_rtl(self):
        path = self._write_tmp(self.SAMPLE_SRT, ".srt")
        subs = parse_subtitles(path)
        subs.wrap_rtl()
        assert "\u202B" in subs[0].text

    def test_normalize_subtitles(self):
        srt = (
            "1\n"
            "00:00:01,000 --> 00:00:04,000\n"
            "الْإِسْلَامُ\n"
        )
        path = self._write_tmp(srt, ".srt")
        subs = parse_subtitles(path)
        subs.normalize()
        assert "ِ" not in subs[0].text
