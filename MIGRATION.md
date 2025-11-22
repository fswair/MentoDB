# Migration Guide: v1.x → v2.0

This guide will help you migrate from MentoDB 1.x to 2.0.

## ⚠️ Breaking Changes Overview

MentoDB 2.0 is a major release with breaking changes focused on security, modernization, and best practices.

### Quick Summary

| Category | v1.x | v2.0 | Impact |
|----------|------|------|--------|
| Python Version | 3.9.6+ | 3.12+ | **HIGH** - Must upgrade Python |
| Pydantic | v1 | v2 | **HIGH** - API changes |
| Security | String formatting | Parameterized queries | **CRITICAL** - SQL injection fixed |
| Dependencies | NumPy required | No NumPy | **LOW** - One less dependency |
| Transactions | Manual | Context managers | **MEDIUM** - API change |
| Exceptions | `BaseException` | `ValueError` | **LOW** - Better error handling |

## 🔒 Security Improvements (CRITICAL)

### SQL Injection Protection

**v1.x** used unsafe string formatting that was vulnerable to SQL injection:

```python
# ❌ v1.x - VULNERABLE
query = f"INSERT INTO {table} VALUES ({user_input})"
```

**v2.0** uses parameterized queries:

```python
# ✅ v2.0 - SECURE
query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
cursor.execute(query, values)
```

**Action Required:** None - automatic upgrade benefit. Your code is now secure by default.

## 🐍 Python Version Upgrade

### Minimum Python 3.12

**Why:** To leverage modern type hints, performance improvements, and better error messages.

**Migration Steps:**

```bash
# Check your Python version
python --version

# If < 3.12, install Python 3.12+
# Ubuntu/Debian
sudo apt install python3.12

# macOS (with Homebrew)
brew install python@3.12

# Windows
# Download from python.org
```

**Update your project:**

```toml
# pyproject.toml
[project]
requires-python = ">=3.12"
```

## 📦 Pydantic v2 Migration

### Schema Access Changes

**v1.x:**
```python
model.__pydantic_model__.schema()
```

**v2.0:**
```python
model.model_fields
```

**Action Required:** If you're accessing Pydantic internals directly, update your code. MentoDB handles this internally, so most users don't need to change anything.

### Model Definition (No Change)

Good news! Model definitions remain the same:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
```

## 🔄 Transaction Management

### Context Managers (Recommended)

**v1.x:**
```python
conn = MentoConnection("db.sqlite")
db = Mento(conn)
try:
    db.insert("users", data={...})
    db.update("users", data={...}, where={...})
    conn.commit()
except Exception:
    # Manual rollback needed
    pass
finally:
    conn.close()
```

**v2.0:**
```python
with MentoConnection("db.sqlite") as conn:
    db = Mento(conn)
    db.insert("users", data={...})
    db.update("users", data={...}, where={...})
    # Auto-commit on success, auto-rollback on error
```

**Action Required:** Wrap your database operations in `with` statements for automatic transaction handling.

### Manual Management (Still Supported)

If you need manual control:

```python
conn = MentoConnection("db.sqlite")
db = Mento(conn)
# ... operations ...
conn.commit()  # or conn.rollback()
conn.close()
```

## 📊 Dependencies

### NumPy Removal

**v1.x:**
```python
from numpy import iterable
```

**v2.0:**
```python
from collections.abc import Iterable
```

**Action Required:** Update your `requirements.txt`:

```diff
- numpy
  pydantic>=2.0.0
  pandas>=2.0.0
```

## ❌ Exception Handling

### Improved Error Messages

**v1.x:**
```python
raise BaseException("Error message")
```

**v2.0:**
```python
raise ValueError("Descriptive error message with context")
```

**Action Required:** Update exception handling:

```python
# v1.x
try:
    db.select(...)
except BaseException as e:
    handle_error(e)

# v2.0
try:
    db.select(...)
except ValueError as e:
    handle_error(e)
```

## 🔧 API Changes

### Delete Method

**v1.x:**
```python
# Default argument was dict()
db.delete("users", where=dict())
```

**v2.0:**
```python
# Default argument is None, must be explicit
db.delete("users", where={"id": 1})
# OR
db.delete("users", delete_all=True)
```

**Action Required:** Ensure `where` parameter is provided or use `delete_all=True`.

### Update Method Parameter Names

**No change** - `data` parameter name remains the same:

```python
# Both versions
db.update("users", data={"age": 31}, where={"id": 1})
```

## 📝 Type Hints

### Modern Syntax (Python 3.12+)

**v2.0** uses modern type hint syntax:

```python
# Union types
def select(...) -> list[dict] | None:
    ...

# Self type
def __enter__(self) -> Self:
    ...
```

**Action Required:** None for usage. If you're extending MentoDB, use modern type hint syntax.

## 🧪 Testing

### New Test Structure

**v1.x:**
- Single `tests.py` file with examples

**v2.0:**
- Full `tests/` directory with pytest
- Comprehensive test coverage
- `pytest-cov` for coverage reports

**Action Required:** Update your test commands:

```bash
# v1.x
python tests.py

# v2.0
pytest
pytest --cov=mentodb
```

## 📦 Installation

### Package Structure

**v2.0** uses modern packaging with `pyproject.toml`:

```bash
# Development install
pip install -e ".[dev]"

# Includes: pytest, black, ruff, mypy, etc.
```

## 🚀 Step-by-Step Migration

### 1. Upgrade Python

```bash
python --version  # Must be 3.12+
```

### 2. Update Dependencies

```bash
# requirements.txt
pydantic>=2.0.0
pandas>=2.0.0
# Remove numpy
```

### 3. Install MentoDB 2.0

```bash
pip install --upgrade mentodb
```

### 4. Update Connection Code

```python
# Before
conn = MentoConnection("db.sqlite")
db = Mento(conn)
# ... operations ...
conn.close()

# After
with MentoConnection("db.sqlite") as conn:
    db = Mento(conn)
    # ... operations ...
```

### 5. Update Exception Handling

```python
# Before
except BaseException:
    ...

# After
except ValueError:
    ...
```

### 6. Test Your Code

```bash
pytest  # Run your tests
```

### 7. Review Security

All SQL injection vulnerabilities are automatically fixed. No action needed!

## 🆘 Common Issues

### Issue: `TypeError: 'Self' is not defined`

**Cause:** Python version < 3.11

**Solution:** Upgrade to Python 3.12+

### Issue: `AttributeError: 'BaseModel' has no attribute '__pydantic_model__'`

**Cause:** Using Pydantic v1

**Solution:** Upgrade to Pydantic v2:
```bash
pip install --upgrade pydantic
```

### Issue: `ModuleNotFoundError: No module named 'numpy'`

**Cause:** NumPy is no longer required

**Solution:** Remove NumPy from requirements, or keep it if needed for other purposes

### Issue: Tests failing after upgrade

**Cause:** API changes

**Solution:** Review this migration guide and update:
1. Exception types (`BaseException` → `ValueError`)
2. Connection management (use context managers)
3. Delete method calls (explicit `where` or `delete_all`)

## 📞 Getting Help

- 🐛 [Report bugs](https://github.com/fswair/MentoDB/issues)
- 💬 [Ask questions](https://github.com/fswair/MentoDB/discussions)
- 📖 [Read CHANGELOG](CHANGELOG.md)

## ✅ Migration Checklist

- [ ] Upgrade Python to 3.12+
- [ ] Update `requirements.txt` (Pydantic v2, remove NumPy)
- [ ] Wrap database operations in `with` statements
- [ ] Update exception handling (`ValueError` instead of `BaseException`)
- [ ] Update delete calls (explicit `where` or `delete_all`)
- [ ] Run tests with pytest
- [ ] Review security improvements
- [ ] Update documentation

---

**Need help?** Open an issue on GitHub or check the [README](README.md) for examples.
