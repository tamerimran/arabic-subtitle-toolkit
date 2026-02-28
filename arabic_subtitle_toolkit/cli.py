"""
Command-line interface for Arabic Subtitle Toolkit.

Usage:
    ast transliterate "بسم الله الرحمن الرحيم" --scheme ala-lc
    ast normalize "الْإِسْلَامُ"
    ast convert video.srt --to vtt --shift 500
    ast info video.srt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from arabic_subtitle_toolkit import __version__
from arabic_subtitle_toolkit.transliteration.engine import (
    transliterate,
    TransliterationScheme,
)
from arabic_subtitle_toolkit.normalization.normalizer import normalize_arabic
from arabic_subtitle_toolkit.subtitles.parser import parse_subtitles


def cmd_transliterate(args: argparse.Namespace) -> None:
    """Handle the 'transliterate' subcommand."""
    result = transliterate(args.text, scheme=args.scheme)
    print(result)


def cmd_normalize(args: argparse.Namespace) -> None:
    """Handle the 'normalize' subcommand."""
    result = normalize_arabic(args.text)
    print(result)


def cmd_convert(args: argparse.Namespace) -> None:
    """Handle the 'convert' subcommand."""
    subs = parse_subtitles(args.input)

    if args.shift:
        subs.shift(args.shift)

    if args.normalize:
        subs.normalize()

    if args.rtl:
        subs.wrap_rtl()

    output = Path(args.output) if args.output else None
    if output is None:
        stem = Path(args.input).stem
        output = Path(f"{stem}.{args.to}")

    subs.save(output, fmt=args.to)
    print(f"Saved: {output} ({len(subs)} entries)")


def cmd_info(args: argparse.Namespace) -> None:
    """Handle the 'info' subcommand."""
    subs = parse_subtitles(args.input)
    arabic_count = sum(1 for e in subs if e.contains_arabic())
    total_dur = subs.entries[-1].end.total_ms if subs.entries else 0
    h, r = divmod(total_dur, 3_600_000)
    m, r = divmod(r, 60_000)
    s = r // 1_000

    print(f"File:            {args.input}")
    print(f"Format:          {subs.source_format}")
    print(f"Total entries:   {len(subs)}")
    print(f"Arabic entries:  {arabic_count}")
    print(f"Duration:        {h:02.0f}:{m:02.0f}:{s:02.0f}")


def main(argv: list[str] | None = None) -> None:
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="ast",
        description="Arabic Subtitle Toolkit – transliterate, normalize, convert",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command")

    # -- transliterate -----------------------------------------------------
    p_trans = sub.add_parser("transliterate", aliases=["tr"], help="Transliterate Arabic text")
    p_trans.add_argument("text", help="Arabic text to transliterate")
    p_trans.add_argument(
        "-s",
        "--scheme",
        default="buckwalter",
        choices=[s.value for s in TransliterationScheme],
        help="Transliteration scheme (default: buckwalter)",
    )
    p_trans.set_defaults(func=cmd_transliterate)

    # -- normalize ---------------------------------------------------------
    p_norm = sub.add_parser("normalize", aliases=["norm"], help="Normalize Arabic text")
    p_norm.add_argument("text", help="Arabic text to normalize")
    p_norm.set_defaults(func=cmd_normalize)

    # -- convert -----------------------------------------------------------
    p_conv = sub.add_parser("convert", help="Convert / transform subtitle files")
    p_conv.add_argument("input", help="Input subtitle file")
    p_conv.add_argument("--to", default="srt", choices=["srt", "vtt"], help="Output format")
    p_conv.add_argument("-o", "--output", help="Output file path")
    p_conv.add_argument("--shift", type=int, help="Shift timestamps by N milliseconds")
    p_conv.add_argument("--normalize", action="store_true", help="Normalize Arabic text")
    p_conv.add_argument("--rtl", action="store_true", help="Add RTL markers to Arabic text")
    p_conv.set_defaults(func=cmd_convert)

    # -- info --------------------------------------------------------------
    p_info = sub.add_parser("info", help="Show subtitle file info")
    p_info.add_argument("input", help="Subtitle file to inspect")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
