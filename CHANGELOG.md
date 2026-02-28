# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-02-28

### Added

- **Transliteration engine** with 4 schemes: Buckwalter, ALA-LC, ISO 233, Simple phonetic
- **Reverse transliteration** (Latin → Arabic) with best-effort mapping
- **Subtitle parser** supporting SRT and WebVTT formats
- **Subtitle manipulation**: shift timestamps, filter Arabic entries, merge files, reindex
- **RTL wrapping** with Unicode directional markers for Arabic subtitle lines
- **Arabic text normalization**: Alef variants, diacritics removal, tatweel stripping, ta marbuta normalization, Ya normalization, Unicode NFC
- **CLI tools**: `ast transliterate`, `ast normalize`, `ast convert`, `ast info`
- **Format conversion**: SRT ↔ WebVTT with full fidelity
- **Comprehensive test suite**: 34 tests covering all modules
- Zero external dependencies — pure Python 3.9+
