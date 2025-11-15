# Changelog

All notable changes to MentoDB will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-15

### 🔒 Security

- **CRITICAL**: Fixed SQL injection vulnerabilities in all query methods
  - All queries now use parameterized statements
  - Added table name validation to prevent injection
  - Column names are validated against table schema

### ✨ Added

- Context manager support for `MentoConnection` (auto-commit/rollback)
- Foreign key support enabled by default
- Connection timeout configuration
- Proper exception handling with specific error types
- Type hints for Python 3.12+ (`Self`, union syntax `|`)
- Modern packaging with `pyproject.toml`
- Comprehensive unit tests with pytest
- Development dependencies for code quality (black, ruff, mypy)

### 🔄 Changed

- **BREAKING**: Migrated to Pydantic v2
  - `__pydantic_model__.schema()` → `model_fields`
  - Updated all Pydantic API usage
- **BREAKING**: Minimum Python version is now 3.12
- Replaced `numpy.iterable()` with `collections.abc.Iterable`
- Replaced `type()` checks with `isinstance()`
- Improved error messages throughout
- Better transaction handling
- `ValueError` instead of `BaseException` for validation errors

### 🗑️ Removed

- NumPy dependency (no longer needed)
- Duplicate `AutoResponse` class definition
- Bare `except` clauses
- Unsafe string formatting in SQL queries

### 🐛 Fixed

- Connection resource leaks
- Inconsistent error handling
- Type annotation issues
- Code duplication

### 📝 Documentation

- Added comprehensive docstrings
- Created CHANGELOG
- Updated README with migration guide
- Added type annotations throughout

### 🏗️ Infrastructure

- Modern `pyproject.toml` configuration
- Pre-commit hooks configuration
- Ruff and Black formatting
- MyPy type checking
- Pytest test suite

## [1.2] - 2022

### Initial Release

- Basic SQLite ORM functionality
- Pydantic v1 integration
- CRUD operations
- Lambda filters
- Regular expression matching
- DataFrame export
