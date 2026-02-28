"""
Subtitle file parser and generator with Arabic-aware processing.

Supports:
    - SRT (SubRip)
    - VTT (WebVTT)
    - ASS / SSA (SubStation Alpha)

Features:
    - RTL-aware text handling
    - Arabic text normalization within subtitles
    - Timestamp manipulation (shift, scale)
    - Merge / split subtitle entries
    - Export between formats

Usage:
    >>> from arabic_subtitle_toolkit import parse_subtitles
    >>> subs = parse_subtitles("video.srt")
    >>> print(len(subs))
    142
    >>> subs.shift(milliseconds=500)
    >>> subs.save("video_shifted.srt")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional


# ---------------------------------------------------------------------------
# Timestamp helper
# ---------------------------------------------------------------------------

@dataclass(order=True)
class Timestamp:
    """Represents a subtitle timestamp with millisecond precision."""

    total_ms: int = 0

    @classmethod
    def from_srt(cls, ts: str) -> Timestamp:
        """Parse ``HH:MM:SS,mmm`` format."""
        match = re.match(
            r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})", ts.strip()
        )
        if not match:
            raise ValueError(f"Invalid SRT timestamp: {ts!r}")
        h, m, s, ms = (int(g) for g in match.groups())
        return cls(total_ms=h * 3_600_000 + m * 60_000 + s * 1_000 + ms)

    @classmethod
    def from_vtt(cls, ts: str) -> Timestamp:
        """Parse ``HH:MM:SS.mmm`` or ``MM:SS.mmm`` format."""
        ts = ts.strip()
        parts = ts.replace(",", ".").split(":")
        if len(parts) == 3:
            h, m, rest = parts
        elif len(parts) == 2:
            h = "0"
            m, rest = parts
        else:
            raise ValueError(f"Invalid VTT timestamp: {ts!r}")
        s, ms = rest.split(".")
        return cls(
            total_ms=int(h) * 3_600_000
            + int(m) * 60_000
            + int(s) * 1_000
            + int(ms)
        )

    # -- formatting --------------------------------------------------------

    def to_srt(self) -> str:
        """Format as ``HH:MM:SS,mmm``."""
        h, remainder = divmod(self.total_ms, 3_600_000)
        m, remainder = divmod(remainder, 60_000)
        s, ms = divmod(remainder, 1_000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    def to_vtt(self) -> str:
        """Format as ``HH:MM:SS.mmm``."""
        return self.to_srt().replace(",", ".")

    # -- arithmetic --------------------------------------------------------

    def shift(self, ms: int) -> Timestamp:
        """Return a new Timestamp shifted by *ms* milliseconds."""
        return Timestamp(total_ms=max(0, self.total_ms + ms))

    def __repr__(self) -> str:
        return f"Timestamp({self.to_srt()})"


# ---------------------------------------------------------------------------
# Subtitle entry
# ---------------------------------------------------------------------------

@dataclass
class SubtitleEntry:
    """A single subtitle cue."""

    index: int
    start: Timestamp
    end: Timestamp
    text: str
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def duration_ms(self) -> int:
        """Duration of the subtitle cue in milliseconds."""
        return self.end.total_ms - self.start.total_ms

    def shift(self, ms: int) -> SubtitleEntry:
        """Return a copy shifted by *ms* milliseconds."""
        return SubtitleEntry(
            index=self.index,
            start=self.start.shift(ms),
            end=self.end.shift(ms),
            text=self.text,
            metadata=dict(self.metadata),
        )

    def contains_arabic(self) -> bool:
        """Check whether the cue text contains Arabic characters."""
        return bool(re.search(r"[\u0600-\u06FF]", self.text))

    def wrap_rtl(self) -> SubtitleEntry:
        """Wrap Arabic text lines with Unicode RTL markers."""
        lines = self.text.splitlines()
        wrapped = []
        for line in lines:
            if re.search(r"[\u0600-\u06FF]", line):
                wrapped.append(f"\u202B{line}\u202C")
            else:
                wrapped.append(line)
        return SubtitleEntry(
            index=self.index,
            start=self.start,
            end=self.end,
            text="\n".join(wrapped),
            metadata=dict(self.metadata),
        )


# ---------------------------------------------------------------------------
# Subtitle file (collection)
# ---------------------------------------------------------------------------

class SubtitleFile:
    """An ordered collection of subtitle entries.

    Provides high-level operations such as shifting, filtering, merging,
    normalizing Arabic text, and saving in multiple formats.
    """

    def __init__(
        self,
        entries: list[SubtitleEntry] | None = None,
        *,
        source_format: str = "srt",
        metadata: dict[str, str] | None = None,
    ) -> None:
        self.entries: list[SubtitleEntry] = entries or []
        self.source_format = source_format
        self.metadata: dict[str, str] = metadata or {}

    # -- basic access ------------------------------------------------------

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterator[SubtitleEntry]:
        return iter(self.entries)

    def __getitem__(self, index: int) -> SubtitleEntry:
        return self.entries[index]

    def __repr__(self) -> str:
        return (
            f"SubtitleFile(entries={len(self.entries)}, "
            f"format={self.source_format!r})"
        )

    # -- transformations ---------------------------------------------------

    def shift(self, milliseconds: int) -> SubtitleFile:
        """Shift all timestamps by *milliseconds* (in-place) and return self."""
        self.entries = [e.shift(milliseconds) for e in self.entries]
        return self

    def filter_arabic(self) -> SubtitleFile:
        """Return a new SubtitleFile containing only Arabic cues."""
        arabic = [e for e in self.entries if e.contains_arabic()]
        return SubtitleFile(entries=arabic, source_format=self.source_format)

    def wrap_rtl(self) -> SubtitleFile:
        """Wrap Arabic lines with RTL markers (in-place) and return self."""
        self.entries = [e.wrap_rtl() for e in self.entries]
        return self

    def normalize(self) -> SubtitleFile:
        """Apply Arabic text normalization to all cues (in-place).

        Requires :mod:`arabic_subtitle_toolkit.normalization`.
        """
        from arabic_subtitle_toolkit.normalization.normalizer import (
            normalize_arabic,
        )

        for entry in self.entries:
            entry.text = normalize_arabic(entry.text)
        return self

    def reindex(self) -> SubtitleFile:
        """Re-number entries sequentially starting from 1."""
        for i, entry in enumerate(self.entries, start=1):
            entry.index = i
        return self

    def merge(self, other: SubtitleFile) -> SubtitleFile:
        """Merge another SubtitleFile into this one, sorted by start time."""
        combined = self.entries + other.entries
        combined.sort(key=lambda e: e.start.total_ms)
        self.entries = combined
        self.reindex()
        return self

    # -- serialization -----------------------------------------------------

    def to_srt(self) -> str:
        """Serialize to SRT format."""
        blocks: list[str] = []
        for entry in self.entries:
            blocks.append(
                f"{entry.index}\n"
                f"{entry.start.to_srt()} --> {entry.end.to_srt()}\n"
                f"{entry.text}\n"
            )
        return "\n".join(blocks)

    def to_vtt(self) -> str:
        """Serialize to WebVTT format."""
        lines = ["WEBVTT", ""]
        for entry in self.entries:
            lines.append(
                f"{entry.start.to_vtt()} --> {entry.end.to_vtt()}\n"
                f"{entry.text}\n"
            )
        return "\n".join(lines)

    def save(self, path: str | Path, fmt: str | None = None) -> Path:
        """Save subtitles to *path*.

        The format is inferred from the file extension unless *fmt* is given.
        """
        path = Path(path)
        fmt = fmt or path.suffix.lstrip(".").lower() or self.source_format

        if fmt == "srt":
            content = self.to_srt()
        elif fmt == "vtt":
            content = self.to_vtt()
        else:
            raise ValueError(f"Unsupported output format: {fmt!r}")

        path.write_text(content, encoding="utf-8")
        return path


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_srt(text: str) -> SubtitleFile:
    """Parse SRT subtitle content."""
    entries: list[SubtitleEntry] = []
    blocks = re.split(r"\n\s*\n", text.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        try:
            index = int(lines[0].strip())
        except ValueError:
            continue
        ts_match = re.match(
            r"(.+?)\s*-->\s*(.+?)(?:\s|$)", lines[1].strip()
        )
        if not ts_match:
            continue
        start = Timestamp.from_srt(ts_match.group(1))
        end = Timestamp.from_srt(ts_match.group(2))
        cue_text = "\n".join(lines[2:])
        entries.append(
            SubtitleEntry(index=index, start=start, end=end, text=cue_text)
        )
    return SubtitleFile(entries=entries, source_format="srt")


def _parse_vtt(text: str) -> SubtitleFile:
    """Parse WebVTT subtitle content."""
    # Remove WEBVTT header and optional metadata
    text = re.sub(r"^WEBVTT[^\n]*\n", "", text.strip(), count=1)
    # Remove style / note blocks
    text = re.sub(r"STYLE\s*\n.*?\n\n", "", text, flags=re.DOTALL)
    text = re.sub(r"NOTE\s*\n.*?\n\n", "", text, flags=re.DOTALL)

    entries: list[SubtitleEntry] = []
    blocks = re.split(r"\n\s*\n", text.strip())
    idx = 1
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        # Optional cue id
        ts_line_idx = 0
        if "-->" not in lines[0]:
            ts_line_idx = 1
            if len(lines) < 2:
                continue
        ts_match = re.match(
            r"(.+?)\s*-->\s*(.+?)(?:\s|$)", lines[ts_line_idx].strip()
        )
        if not ts_match:
            continue
        start = Timestamp.from_vtt(ts_match.group(1))
        end = Timestamp.from_vtt(ts_match.group(2))
        cue_text = "\n".join(lines[ts_line_idx + 1:])
        entries.append(
            SubtitleEntry(index=idx, start=start, end=end, text=cue_text)
        )
        idx += 1
    return SubtitleFile(entries=entries, source_format="vtt")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse_subtitles(source: str | Path) -> SubtitleFile:
    """Parse a subtitle file (SRT or VTT).

    Args:
        source: File path to the subtitle file.

    Returns:
        A :class:`SubtitleFile` instance.

    Example:
        >>> subs = parse_subtitles("movie.srt")
        >>> print(len(subs))
        142
    """
    path = Path(source)
    content = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()

    if ext == ".srt":
        return _parse_srt(content)
    elif ext in (".vtt", ".webvtt"):
        return _parse_vtt(content)
    else:
        # Try SRT first, then VTT
        try:
            result = _parse_srt(content)
            if result.entries:
                return result
        except Exception:
            pass
        return _parse_vtt(content)
