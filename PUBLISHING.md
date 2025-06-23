# Publishing Guide

This guide explains how to publish the `python-result-type` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **Test PyPI Account**: Create an account at https://test.pypi.org/account/register/
3. **API Tokens**: 
   - Create a Test PyPI token at https://test.pypi.org/manage/account/#api-tokens
   - Create a PyPI token at https://pypi.org/manage/account/#api-tokens

## Setup

1. **Clone and Setup Environment**:
   ```bash
   git clone <repository-url>
   cd python-result-type
   python3 -m venv venv
   source venv/bin/activate
   pip install build twine pytest
   ```

2. **Run Tests**:
   ```bash
   python -m pytest tests/ -v
   ```

3. **Update Version** (if needed):
   - Update version in `pyproject.toml`
   - Update version in `result_type/__init__.py`

## Publishing Process

### Option 1: Using Makefile Commands

```bash
# Test the package
make test

# Build the package
make build

# Upload to Test PyPI first
make upload-test

# Upload to PyPI
make upload
```

### Option 2: Manual Commands

1. **Clean Previous Builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

2. **Build the Package**:
   ```bash
   python -m build
   ```

3. **Upload to Test PyPI** (recommended first):
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```
   - Enter your Test PyPI API token when prompted
   - Verify at https://test.pypi.org/project/python-result-type/

4. **Test Installation from Test PyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ python-result-type
   ```

5. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```
   - Enter your PyPI API token when prompted
   - Verify at https://pypi.org/project/python-result-type/

## API Token Configuration

For easier publishing, you can configure your tokens in `~/.pypirc`:

```ini
[distutils]
index-servers = 
  pypi
  testpypi

[pypi]
  username = __token__
  password = pypi-your-api-token-here

[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = pypi-your-test-api-token-here
```

## Version Management

When releasing a new version:

1. Update the version number in:
   - `pyproject.toml` (line 7)
   - `result_type/__init__.py` (line 43)

2. Update the changelog/release notes in README.md

3. Create a git tag:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

## Troubleshooting

- **403 Forbidden**: Check your API token and permissions
- **Package already exists**: Increment the version number
- **Build errors**: Check that venv/ and other build artifacts are excluded
- **Import errors**: Ensure all dependencies are listed in pyproject.toml

## Security Notes

- Never commit API tokens to version control
- Use scoped tokens with minimal required permissions
- Regularly rotate your API tokens
