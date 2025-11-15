# Changelog

All notable changes to MentoDB will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2025-11-15

### 🎯 API Improvements

- **BREAKING (with backward compatibility)**: Renamed connection classes for clarity
  - `MentoConnection` → `Connection` (cleaner, more standard)
  - `AsyncMentoConnection` → `AsyncConnection` (shorter, consistent)
  - Old names still work as aliases but are deprecated (will be removed in v3.0)

### 🏗️ Project Structure

- **Reorganized to professional `src/` layout**
  - Moved all modules to `src/mentodb/`
  - Organized into logical submodules:
    - `core/` - Core ORM functionality (Connection, Mento, etc.)
    - `async_api/` - Async database operations
    - `query/` - Query building tools
    - `migrations/` - Schema versioning
    - `schema/` - Indexes & relationships
    - `performance/` - Optimization features (pool, bulk, cache)
  - Each submodule has clear purpose and `__init__.py`
  - Follows modern Python packaging best practices (PEP 420)

### 🔄 Changed

- Updated all internal imports to use new names
- Updated examples to demonstrate new API
- Updated tests to use new connection classes
- Updated `pyproject.toml` for src layout (`package-dir`, `packages.find`)

### 📝 Migration Guide

```python
# Old (still works, but deprecated)
from mentodb import MentoConnection, AsyncMentoConnection

# New (recommended)
from mentodb import Connection, AsyncConnection
```

## [2.1.0] - 2025-11-15

### 🚀 Major Features

- **Async Support** - Full async/await support with `AsyncMentoConnection`
  - Use `aiosqlite` for async database operations
  - Compatible with `asyncio` applications
  - Context manager support with `async with`

- **Query Builder** - Fluent API for building SQL queries
  - Method chaining for readable queries
  - Support for complex joins, subqueries, and aggregations
  - Automatic parameter binding
  - Example: `QueryBuilder("users").select("*").where("age", ">", 18).limit(10).build()`

- **Database Migrations** - Schema versioning and migration system
  - Track database schema changes
  - Apply/rollback migrations
  - Export/import schema
  - Migration status tracking

- **Connection Pooling** - Thread-safe connection pool
  - Reuse connections efficiently
  - Configurable pool size
  - Automatic connection management

- **Relationships** - Foreign key and JOIN support
  - Define and manage foreign keys
  - One-to-one, one-to-many, many-to-many relationships
  - Simplified JOIN queries
  - Foreign key constraint validation

- **Index Management** - Create and manage database indexes
  - Create/drop indexes programmatically
  - List all indexes
  - Analyze index performance
  - Support for unique indexes

- **Bulk Operations** - Efficient batch processing
  - Bulk insert (batch import)
  - Bulk update
  - Bulk delete
  - Bulk upsert (INSERT OR REPLACE)
  - Configurable batch sizes

- **Query Caching** - LRU cache with TTL support
  - Cache query results for performance
  - Configurable cache size and TTL
  - Automatic cache invalidation
  - Cache statistics and hit/miss tracking

### ✨ Added

- `AsyncMentoConnection` - Async connection wrapper
- `QueryBuilder` - Fluent query builder
- `Migration` and `MigrationManager` - Migration system
- `ConnectionPool` - Connection pooling
- `RelationshipManager` and `ForeignKey` - Relationship management
- `IndexManager` - Index management
- `BulkOperations` - Batch operations
- `QueryCache` and `CachedConnection` - Result caching
- New dependency: `aiosqlite>=0.19.0`

### 📝 Documentation

- Updated README with new features
- Added examples for all new features
- Updated API documentation

### 🔄 Changed

- Version bumped to 2.1.0
- Updated package description
- Added new keywords for discoverability

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
