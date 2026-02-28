"""
Batch processing utilities for subtitle workflows.

Process entire directories of subtitle files with a single function call.
Useful for content creators managing multilingual subtitle libraries.

Usage:
    >>> from arabic_subtitle_toolkit.batch import batch_normalize, batch_convert
    >>> results = batch_normalize("./subtitles/", output_dir="./cleaned/")
    >>> print(f"Processed {len(results)} files")
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from arabic_subtitle_toolkit.subtitles.parser import SubtitleFile, parse_subtitles


@dataclass
class BatchResult:
    """Result of processing a single file in a batch operation."""

    source: Path
    output: Path | None
    success: bool
    entries_count: int
    error: str | None = None


def batch_process(
    input_dir: str | Path,
    output_dir: str | Path | None = None,
    *,
    transform: Callable[[SubtitleFile], SubtitleFile] | None = None,
    output_format: str | None = None,
    extensions: tuple[str, ...] = (".srt", ".vtt"),
    recursive: bool = False,
) -> list[BatchResult]:
    """Process multiple subtitle files with a custom transformation.

    Args:
        input_dir: Directory containing subtitle files.
        output_dir: Directory for output files (default: overwrite in place).
        transform: A callable that transforms a SubtitleFile and returns it.
        output_format: Output format override (e.g., ``"vtt"``).
        extensions: File extensions to include.
        recursive: If True, search subdirectories recursively.

    Returns:
        List of :class:`BatchResult` objects.

    Example:
        >>> results = batch_process(
        ...     "./subs/",
        ...     output_dir="./cleaned/",
        ...     transform=lambda s: s.normalize().wrap_rtl(),
        ... )
    """
    input_path = Path(input_dir)
    out_path = Path(output_dir) if output_dir else None

    if out_path:
        out_path.mkdir(parents=True, exist_ok=True)

    if recursive:
        files = [
            p
            for ext in extensions
            for p in input_path.rglob(f"*{ext}")
            if p.is_file()
        ]
    else:
        files = [
            p
            for p in input_path.iterdir()
            if p.is_file() and p.suffix.lower() in extensions
        ]

    files.sort()
    results: list[BatchResult] = []

    for filepath in files:
        try:
            subs = parse_subtitles(filepath)

            if transform:
                subs = transform(subs)

            fmt = output_format or filepath.suffix.lstrip(".").lower()
            if out_path:
                dest = out_path / f"{filepath.stem}.{fmt}"
            else:
                dest = filepath.with_suffix(f".{fmt}")

            subs.save(dest, fmt=fmt)
            results.append(
                BatchResult(
                    source=filepath,
                    output=dest,
                    success=True,
                    entries_count=len(subs),
                )
            )
        except Exception as e:
            results.append(
                BatchResult(
                    source=filepath,
                    output=None,
                    success=False,
                    entries_count=0,
                    error=str(e),
                )
            )

    return results


def batch_normalize(
    input_dir: str | Path,
    output_dir: str | Path | None = None,
    **kwargs,
) -> list[BatchResult]:
    """Normalize Arabic text in all subtitle files in a directory.

    Args:
        input_dir: Directory containing subtitle files.
        output_dir: Output directory (default: overwrite in place).
        **kwargs: Additional arguments passed to :func:`batch_process`.

    Returns:
        List of :class:`BatchResult` objects.
    """
    return batch_process(
        input_dir,
        output_dir,
        transform=lambda s: s.normalize(),
        **kwargs,
    )


def batch_convert(
    input_dir: str | Path,
    output_dir: str | Path,
    output_format: str = "vtt",
    **kwargs,
) -> list[BatchResult]:
    """Convert all subtitle files in a directory to a different format.

    Args:
        input_dir: Directory containing subtitle files.
        output_dir: Output directory for converted files.
        output_format: Target format (``"srt"`` or ``"vtt"``).
        **kwargs: Additional arguments passed to :func:`batch_process`.

    Returns:
        List of :class:`BatchResult` objects.
    """
    return batch_process(
        input_dir,
        output_dir,
        output_format=output_format,
        **kwargs,
    )
