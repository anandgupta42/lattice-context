# Release Checklist - Lattice Context Layer

## Pre-Release Checklist

### Code Quality
- [x] All tests passing (`pytest tests/ -v`)
- [x] No critical bugs
- [x] Ruff linting clean
- [x] Type hints throughout
- [x] Error handling comprehensive

### Documentation
- [x] README.md up to date
- [x] QUICKSTART.md complete
- [x] LICENSE file present (MIT)
- [x] All CLI commands documented
- [x] Error messages helpful

### Package
- [x] pyproject.toml metadata correct
- [x] MANIFEST.in configured
- [x] Package builds: `python -m build`
- [x] Package checks: `twine check dist/*`
- [x] Dependencies minimal and correct

### Testing
- [x] Test in fresh virtual environment
- [x] Test installation from wheel
- [x] Test all CLI commands
- [x] Test with sample dbt project
- [ ] Test with Claude Desktop (manual)

## Release Process

### 1. Version Bump
```bash
# Update version in pyproject.toml
# Format: 0.1.0, 0.2.0, 1.0.0, etc.
```

### 2. Build Package
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Verify
twine check dist/*
```

### 3. Test Installation
```bash
# Create test environment
python3.12 -m venv test-venv
source test-venv/bin/activate

# Install from wheel
pip install dist/lattice_context-*.whl

# Test
lattice --help
cd /path/to/test/dbt/project
lattice init
lattice index
lattice context "test query"

# Cleanup
deactivate
rm -rf test-venv
```

### 4. Git Tag
```bash
# Create tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"

# Push tag
git push origin v0.1.0
```

### 5. GitHub Release
- Go to GitHub Releases
- Click "Draft a new release"
- Select tag v0.1.0
- Title: "v0.1.0 - Initial Release"
- Description:
  ```markdown
  ## Lattice Context Layer v0.1.0

  First public release! 🎉

  ### Features
  - Zero-config dbt project detection
  - Fast indexing (<30s for 100 models)
  - Intelligent context retrieval
  - User correction system
  - MCP server for Claude Desktop
  - Structured logging

  ### Installation
  \`\`\`bash
  pip install lattice-context
  \`\`\`

  See [README.md](README.md) for quickstart guide.
  ```
- Attach dist files
- Publish release

### 6. PyPI Publication
Publishing happens automatically via GitHub Action when release is published.

**Manual upload (if needed):**
```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ lattice-context

# If successful, upload to real PyPI
twine upload dist/*
```

### 7. Verify PyPI
- Check https://pypi.org/project/lattice-context/
- Verify description renders correctly
- Test installation: `pip install lattice-context`

### 8. Announce
- [ ] Update README with pip install command
- [ ] Post on dbt Slack #tools-showcase
- [ ] Post on Reddit r/dataengineering
- [ ] Tweet announcement
- [ ] Update project documentation

## Post-Release

### Monitor
- [ ] Watch for GitHub issues
- [ ] Check PyPI download stats
- [ ] Monitor error reports
- [ ] Collect user feedback

### Documentation
- [ ] Update CHANGELOG.md
- [ ] Document known issues
- [ ] Add FAQ based on questions

## Rollback Plan

If critical issues found after release:

1. Yank bad version from PyPI:
   ```bash
   # This prevents new installs but doesn't break existing
   twine upload --skip-existing --repository pypi dist/*
   ```

2. Fix issue in new patch version (e.g., 0.1.1)

3. Release patch following this checklist

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 0.1.0 | TBD | Initial public release |

## Support Plan

### Issues
- Respond to GitHub issues within 24 hours
- Critical bugs: hotfix within 48 hours
- Feature requests: evaluate and prioritize

### Documentation
- Keep README updated with common issues
- Add examples based on user questions
- Update QUICKSTART for clarity

### Community
- Monitor dbt Slack for mentions
- Engage with users on Reddit/Twitter
- Collect testimonials and use cases
