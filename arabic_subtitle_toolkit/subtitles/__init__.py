"""Arabic subtitle parsing subpackage."""

from arabic_subtitle_toolkit.subtitles.parser import (
    parse_subtitles,
    SubtitleFile,
    SubtitleEntry,
    Timestamp,
)

__all__ = ["parse_subtitles", "SubtitleFile", "SubtitleEntry", "Timestamp"]
