# 🌍 Arabic Subtitle Toolkit

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-40%20passing-brightgreen.svg)]()

A comprehensive Python toolkit for Arabic subtitle processing, transliteration, and text normalization — built for content creators, developers, and researchers working with Arabic media.

## Why?

The Arabic-speaking world represents **400+ million speakers** across 25+ countries, yet tooling for Arabic subtitle processing is fragmented and often broken. Content creators serving Arabic audiences face unique challenges:

- **RTL text handling** in subtitle formats designed for LTR languages
- **Transliteration inconsistencies** across academic and industry standards
- **Diacritics and normalization** issues that break search and matching
- **No unified library** that handles subtitles + transliteration + normalization together

This toolkit solves all of these in a single, zero-dependency Python package.

## Features

| Feature | Description |
|---|---|
| **Transliteration** | Arabic ↔ Latin with 4 schemes: Buckwalter, ALA-LC, ISO 233, Simple |
| **Subtitle Parsing** | Read & write SRT, WebVTT with full timestamp manipulation |
| **Normalization** | Alef variants, diacritics, tatweel, ta marbuta, Unicode NFC |
| **RTL Wrapping** | Automatic Unicode RTL markers for Arabic subtitle lines |
| **CLI** | Command-line tools for batch processing workflows |
| **Batch Processing** | Directory-level operations with custom transform pipelines |
| **Zero Dependencies** | Pure Python — no external packages required |

## Installation

```bash
pip install arabic-subtitle-toolkit
```

Or install from source:

```bash
git clone https://github.com/tamerimran/arabic-subtitle-toolkit.git
cd arabic-subtitle-toolkit
pip install -e .
```

## Quick Start

### Transliteration

```python
from arabic_subtitle_toolkit import transliterate

# Buckwalter (default) — standard in NLP
transliterate("بسم الله الرحمن الرحيم")
# → 'bsm Allh AlrHmn AlrHym'

# ALA-LC — Library of Congress standard
transliterate("بسم الله الرحمن الرحيم", scheme="ala-lc")
# → 'bismi allāhi al-raḥmāni al-raḥīmi'

# Simple phonetic — for general audiences
transliterate("السلام عليكم", scheme="simple")
# → 'as-salaam alaykum'

# Reverse transliteration (Latin → Arabic)
from arabic_subtitle_toolkit import Transliterator, TransliterationScheme
t = Transliterator(scheme=TransliterationScheme.BUCKWALTER)
t.reverse("ktb")
# → 'كتب'
```

### Subtitle Processing

```python
from arabic_subtitle_toolkit import parse_subtitles

# Parse any subtitle file (SRT, VTT)
subs = parse_subtitles("my_video.srt")
print(f"Found {len(subs)} subtitle entries")

# Shift all timestamps by 2 seconds
subs.shift(milliseconds=2000)

# Normalize Arabic text in all entries
subs.normalize()

# Add RTL markers for proper display
subs.wrap_rtl()

# Filter to Arabic-only entries
arabic_subs = subs.filter_arabic()

# Convert SRT → WebVTT
subs.save("my_video.vtt")

# Merge two subtitle files
subs2 = parse_subtitles("another.srt")
subs.merge(subs2)
subs.save("merged.srt")
```

### Text Normalization

```python
from arabic_subtitle_toolkit import normalize_arabic

# Remove diacritics and normalize Alef variants
normalize_arabic("الْإِسْلَامُ")
# → 'الاسلام'

# Remove tatweel (kashida)
normalize_arabic("كتـــاب")
# → 'كتاب'

# Fine-grained control
from arabic_subtitle_toolkit import ArabicNormalizer
n = ArabicNormalizer(
    normalize_alef=True,
    remove_diacritics=True,
    remove_tatweel=True,
    normalize_ta_marbuta=False,  # preserve meaning
)
n.normalize("الْإِسْلَامُ")
```

### Batch Processing

```python
from arabic_subtitle_toolkit import batch_normalize, batch_convert

# Normalize all Arabic subtitles in a directory
results = batch_normalize("./raw_subs/", output_dir="./clean_subs/")
print(f"Processed {len(results)} files")

# Convert entire SRT library to WebVTT
results = batch_convert("./srt_files/", "./vtt_output/", output_format="vtt")

# Custom pipeline with recursive directory search
from arabic_subtitle_toolkit import batch_process
results = batch_process(
    "./subtitles/",
    "./output/",
    transform=lambda s: s.normalize().wrap_rtl().shift(500),
    recursive=True,
)
```

## CLI Usage

```bash
# Transliterate text
ast transliterate "بسم الله" --scheme ala-lc

# Normalize text
ast normalize "الْإِسْلَامُ"

# Convert subtitle formats
ast convert video.srt --to vtt

# Shift subtitles by 500ms
ast convert video.srt --to srt --shift 500

# Normalize Arabic + add RTL markers
ast convert video.srt --to srt --normalize --rtl

# Show subtitle file info
ast info video.srt
```

## Transliteration Schemes

| Scheme | Use Case | Example (كتاب) |
|---|---|---|
| `buckwalter` | NLP, computational linguistics | `ktAb` |
| `ala-lc` | Libraries, academic publishing | `ktāb` |
| `iso-233` | International standards compliance | `ktāb` |
| `simple` | General audiences, phonetic | `ktab` |

## Use Cases

- **YouTube creators** producing Arabic content with multilingual subtitles
- **Media companies** processing Arabic-language video at scale
- **NLP researchers** needing consistent Arabic text preprocessing
- **Localization teams** working with RTL subtitle workflows
- **Accessibility tools** generating transliterated captions for non-Arabic speakers
- **Educational platforms** serving Arabic-speaking learners globally

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Run tests
pip install pytest
pytest

# Lint
pip install ruff
ruff check .
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

Built by [Tamer](https://github.com/tamerimran) — a content creator and AI specialist with 30+ years of experience building tools for Arabic-language media and education.
