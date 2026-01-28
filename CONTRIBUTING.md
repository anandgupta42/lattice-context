# Contributing to Lattice Context Layer

Thank you for your interest in contributing to Lattice Context Layer! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/lattice-context.git
   cd lattice-context
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/anandgupta42/lattice-context.git
   ```

## Development Setup

### Prerequisites

- Python 3.10, 3.11, or 3.12
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev,llm,mcp,web]"
   ```

3. **Verify installation**:
   ```bash
   pytest tests/
   lattice --help
   ```

## How to Contribute

### Reporting Bugs

Before creating a bug report:
- Check existing issues to avoid duplicates
- Use the latest version to verify the bug still exists

When filing a bug report, include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Include:
- Clear use case and problem being solved
- Proposed solution or implementation approach
- Why this would be useful to other users

### Good First Issues

Look for issues tagged with `good first issue` for beginner-friendly contributions.

## Coding Standards

### Python Style

We follow PEP 8 with these tools:
- **Formatter**: `ruff format`
- **Linter**: `ruff check`

Run before committing:
```bash
ruff format src/ tests/
ruff check src/ tests/
```

### Type Hints

- Use type hints for all function signatures
- Use `from __future__ import annotations` for forward references
- Run `mypy` for type checking (configured in `pyproject.toml`)

### Code Organization

- Keep functions small and focused (single responsibility)
- Use descriptive variable and function names
- Add docstrings for public functions and classes
- Group imports: standard library, third-party, local

### Example

```python
from typing import Optional

def extract_decisions(
    commits: list[Commit],
    llm_client: Optional[LLMClient] = None
) -> list[Decision]:
    """
    Extract decisions from git commits.

    Args:
        commits: List of git commits to analyze
        llm_client: Optional LLM client for enhanced extraction

    Returns:
        List of extracted decisions

    Raises:
        ExtractionError: If extraction fails critically
    """
    # Implementation here
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_cli.py

# Run with coverage
pytest tests/ --cov=lattice_context --cov-report=html
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what's being tested

Example:
```python
def test_init_command_creates_lattice_directory(tmp_path):
    """Test that 'lattice init' creates .lattice directory."""
    result = runner.invoke(app, ["init"], cwd=tmp_path)
    assert result.exit_code == 0
    assert (tmp_path / ".lattice").exists()
```

### Test Coverage

- Aim for >80% coverage on new code
- All new features must include tests
- Bug fixes should include regression tests

## Documentation

### User Documentation

Update these files for user-facing changes:
- `README.md` - Overview and quickstart
- `QUICKSTART.md` - Detailed getting started guide
- `FEATURES.md` - Feature catalog
- `CHANGELOG.md` - Keep a Changelog format

### Technical Documentation

For API changes or new integrations:
- `docs/COPILOT_INTEGRATION.md` - GitHub Copilot API
- `docs/UNIVERSAL_API.md` - Universal context API
- Integration-specific READMEs in `integrations/`

### Code Comments

- Use comments to explain **why**, not **what**
- Document non-obvious design decisions
- Add TODOs with issue references: `# TODO(#123): Implement caching`

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests and linting**:
   ```bash
   pytest tests/
   ruff format src/ tests/
   ruff check src/ tests/
   ```

3. **Update documentation** if needed

4. **Update CHANGELOG.md** under "Unreleased" section

### Creating PR

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make commits** with clear messages:
   ```
   Add context caching for repeated queries

   - Implement LRU cache with 100-item limit
   - Add cache hit/miss metrics
   - Update tests for caching behavior

   Closes #123
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open Pull Request** on GitHub:
   - Use descriptive title
   - Reference related issues
   - Explain what and why (not how - code shows how)
   - Add screenshots for UI changes
   - Mark as draft if work in progress

### PR Requirements

All PRs must:
- ✅ Pass all tests
- ✅ Pass linting checks
- ✅ Include tests for new code
- ✅ Update documentation
- ✅ Follow coding standards
- ✅ Have clear commit messages

### Review Process

- Maintainers will review within 48 hours
- Address review comments
- Keep discussion professional and constructive
- CI must pass before merge

## Development Workflow

### Feature Development

```bash
# 1. Create branch from main
git checkout main
git pull upstream main
git checkout -b feature/awesome-feature

# 2. Develop with tests
# ... make changes ...
pytest tests/

# 3. Commit changes
git add .
git commit -m "Add awesome feature"

# 4. Push and create PR
git push origin feature/awesome-feature
# Open PR on GitHub
```

### Bug Fixes

```bash
# 1. Create branch
git checkout -b fix/bug-description

# 2. Write failing test that reproduces bug
# 3. Fix the bug
# 4. Verify test now passes
# 5. Submit PR
```

## Project Structure

```
lattice-context/
├── src/lattice_context/      # Main package
│   ├── cli/                   # CLI commands
│   ├── core/                  # Core business logic
│   ├── extractors/            # Data extractors (dbt, git)
│   ├── integrations/          # Tool integrations
│   ├── mcp/                   # MCP server
│   ├── storage/               # Database layer
│   └── web/                   # Web dashboard
├── tests/                     # Test suite
├── docs/                      # Documentation
├── integrations/              # Integration guides
└── vscode-extension/          # VS Code extension
```

## Release Process

Maintainers handle releases:
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with release date
3. Create git tag: `git tag -a v0.x.0 -m "Release v0.x.0"`
4. Push tag: `git push origin v0.x.0`
5. GitHub Actions publishes to PyPI automatically

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Chat**: (Coming soon)
- **Email**: hello@altimate.ai

## Recognition

Contributors will be:
- Listed in release notes
- Added to AUTHORS file
- Credited in commit co-authorship

Thank you for contributing! 🎉
