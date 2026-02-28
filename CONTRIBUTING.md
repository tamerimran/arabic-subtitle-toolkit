# Contributing to Arabic Subtitle Toolkit

Thank you for considering contributing! This project serves the Arabic-speaking content creation community, and every contribution helps.

## How to Contribute

### Reporting Bugs

- Open an [issue](https://github.com/tamerimran/arabic-subtitle-toolkit/issues) with a clear description
- Include: Python version, OS, minimal reproduction steps, expected vs actual behavior

### Suggesting Features

- Open an issue with the `enhancement` label
- Describe the use case and why it would benefit Arabic content workflows

### Submitting Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Write tests for your changes
4. Ensure all tests pass: `pytest`
5. Lint your code: `ruff check .`
6. Submit a pull request

### Code Style

- Follow PEP 8 (enforced via Ruff)
- Type hints on all public APIs
- Docstrings (Google style) on all public functions and classes
- Tests for all new functionality

### Areas Where Help Is Needed

- **ASS/SSA subtitle format** parsing and generation
- **Additional transliteration schemes** (e.g., DIN 31635, UN romanization)
- **Dialect-specific normalization** (Egyptian, Gulf, Levantine, Maghrebi)
- **Performance optimization** for large subtitle files
- **Documentation** improvements and more examples
- **Translations** of documentation into Arabic

## Development Setup

```bash
git clone https://github.com/tamerimran/arabic-subtitle-toolkit.git
cd arabic-subtitle-toolkit
pip install -e ".[dev]"
pytest
```

## Code of Conduct

Be respectful, inclusive, and constructive. We welcome contributors of all backgrounds and experience levels.
