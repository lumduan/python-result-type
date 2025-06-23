# Pre-Publication Checklist

Use this checklist before publishing your package to PyPI.

## ✅ Code Quality

- [ ] All tests pass (`make test` or `python -m pytest tests/ -v`)
- [ ] Code is properly formatted (`make format` or `black result_type tests`)
- [ ] No linting errors (`make lint` or `ruff check result_type tests`)
- [ ] Type checking passes (`make type-check` or `mypy result_type`)

## ✅ Documentation

- [ ] README.md is complete and accurate
- [ ] All examples in README.md work correctly
- [ ] Docstrings are comprehensive and accurate
- [ ] CHANGELOG.md is updated (if you have one)

## ✅ Package Configuration

- [ ] Version number updated in `pyproject.toml`
- [ ] Version number updated in `result_type/__init__.py`
- [ ] Author information is correct in `pyproject.toml`
- [ ] Project URLs are correct in `pyproject.toml`
- [ ] Dependencies are correctly listed
- [ ] Supported Python versions are accurate

## ✅ Legal and Licensing

- [ ] LICENSE file exists and is appropriate
- [ ] All code is original or properly attributed
- [ ] No copyrighted material included without permission

## ✅ PyPI Setup

- [ ] PyPI account created at https://pypi.org/
- [ ] Test PyPI account created at https://test.pypi.org/
- [ ] API tokens generated for both PyPI and Test PyPI
- [ ] Package name `python-result-type` is available on PyPI

## ✅ Build and Test

- [ ] Package builds successfully (`make build` or `python -m build`)
- [ ] No build warnings or errors
- [ ] Distribution files created in `dist/` directory
- [ ] Test upload to Test PyPI works
- [ ] Can install from Test PyPI successfully

## ✅ Final Steps

- [ ] Git repository is clean (no uncommitted changes)
- [ ] All changes are pushed to remote repository
- [ ] Git tag created for release (e.g., `git tag v1.0.0`)
- [ ] Ready to upload to production PyPI

## Publishing Commands

### Test Upload (Do this first!)
```bash
./publish.sh  # Select option 1
# OR
make upload-test
```

### Production Upload
```bash
./publish.sh  # Select option 2
# OR  
make upload
```

### Verify Installation
After uploading, test that users can install your package:
```bash
pip install python-result-type
python -c "from result_type import Success, Failure; print('✅ Package works!')"
```
