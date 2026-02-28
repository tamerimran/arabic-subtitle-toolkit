"""Tests for batch processing utilities."""

import tempfile
from pathlib import Path

import pytest

from arabic_subtitle_toolkit.batch import (
    batch_process,
    batch_normalize,
    batch_convert,
)


SAMPLE_SRT_1 = (
    "1\n"
    "00:00:01,000 --> 00:00:04,000\n"
    "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\n"
    "\n"
    "2\n"
    "00:00:05,000 --> 00:00:08,000\n"
    "In the name of God\n"
)

SAMPLE_SRT_2 = (
    "1\n"
    "00:00:01,000 --> 00:00:03,000\n"
    "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ\n"
)


class TestBatchProcessing:
    """Tests for batch operations."""

    def _setup_dir(self, files: dict[str, str]) -> Path:
        """Create a temp dir with subtitle files."""
        d = Path(tempfile.mkdtemp())
        for name, content in files.items():
            (d / name).write_text(content, encoding="utf-8")
        return d

    def test_batch_normalize(self):
        src = self._setup_dir({
            "video1.srt": SAMPLE_SRT_1,
            "video2.srt": SAMPLE_SRT_2,
        })
        out = Path(tempfile.mkdtemp())
        results = batch_normalize(src, out)
        assert len(results) == 2
        assert all(r.success for r in results)
        # Check diacritics removed
        content = (out / "video1.srt").read_text(encoding="utf-8")
        assert "ِ" not in content

    def test_batch_convert_srt_to_vtt(self):
        src = self._setup_dir({"video1.srt": SAMPLE_SRT_1})
        out = Path(tempfile.mkdtemp())
        results = batch_convert(src, out, output_format="vtt")
        assert len(results) == 1
        assert results[0].success
        vtt = (out / "video1.vtt").read_text(encoding="utf-8")
        assert "WEBVTT" in vtt

    def test_batch_process_custom_transform(self):
        src = self._setup_dir({"video1.srt": SAMPLE_SRT_1})
        out = Path(tempfile.mkdtemp())
        results = batch_process(
            src, out,
            transform=lambda s: s.normalize().wrap_rtl(),
        )
        assert len(results) == 1
        assert results[0].success
        assert results[0].entries_count == 2

    def test_batch_skips_non_subtitle_files(self):
        src = self._setup_dir({
            "video1.srt": SAMPLE_SRT_1,
            "notes.txt": "just some notes",
        })
        out = Path(tempfile.mkdtemp())
        results = batch_normalize(src, out)
        assert len(results) == 1  # only .srt processed

    def test_batch_handles_errors_gracefully(self):
        src = self._setup_dir({
            "good.srt": SAMPLE_SRT_1,
            "bad.srt": "this is not valid subtitle content\nno timestamps here",
        })
        out = Path(tempfile.mkdtemp())
        results = batch_normalize(src, out)
        assert len(results) == 2
        # At least the good one should succeed
        good = [r for r in results if "good" in str(r.source)]
        assert good[0].success

    def test_batch_recursive(self):
        base = Path(tempfile.mkdtemp())
        sub = base / "season1"
        sub.mkdir()
        (base / "intro.srt").write_text(SAMPLE_SRT_1, encoding="utf-8")
        (sub / "ep01.srt").write_text(SAMPLE_SRT_2, encoding="utf-8")
        out = Path(tempfile.mkdtemp())
        results = batch_normalize(base, out, recursive=True)
        assert len(results) == 2
