# MentoDB 🗄️

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/pypi/v/mentodb.svg)](https://pypi.org/project/mentodb/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modern, type-safe SQLite ORM for Python with Pydantic integration. Built for simplicity, security, and developer experience.

## ✨ Features

- 🔒 **Secure by Default** - Parameterized queries prevent SQL injection
- 🎯 **Type-Safe** - Full type hints with Pydantic v2 integration
- 🚀 **Modern Python** - Leverages Python 3.12+ features
- 🔄 **Context Managers** - Automatic transaction handling
- 📊 **Multiple Export Formats** - JSON, Pandas DataFrame, or Pydantic models
- 🧪 **Well Tested** - Comprehensive test suite with pytest
- 🎨 **Clean API** - Intuitive, Pythonic interface
- ⚡ **Zero Config** - Works out of the box

## 📦 Installation

```bash
pip install mentodb
```

**Requirements:**
- Python 3.12 or higher
- Pydantic 2.0+
- Pandas 2.0+

## 🚀 Quick Start

```python
from mentodb import Mento, MentoConnection
from pydantic import BaseModel

# Define your model
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int

# Create connection with context manager
with MentoConnection("myapp.db") as conn:
    db = Mento(conn, default_table="users")

    # Create table
    db.create("users", model=User)

    # Insert data
    db.insert("users", data={
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30
    })

    # Query data
    users = db.select(from_table="users", where={"name": "Alice"})
    print(users)  # [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'age': 30}]
```

## 📖 Documentation

### Creating Tables

```python
from mentodb import Mento, MentoConnection, PrimaryKey
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int

with MentoConnection("store.db") as conn:
    db = Mento(conn)
    db.create("products", model=Product)
```

### CRUD Operations

#### Insert

```python
# Single insert
db.insert("products", data={
    "id": 1,
    "name": "Laptop",
    "price": 999.99,
    "stock": 50
})
```

#### Select

```python
# Select all
all_products = db.select(from_table="products")

# Select with WHERE clause
laptops = db.select(
    from_table="products",
    where={"name": "Laptop"}
)

# Select with ORDER BY and LIMIT
top_products = db.select(
    from_table="products",
    order_by="price",
    limit=10
)

# Select specific columns
names = db.select(
    from_table="products",
    select_column="name"
)
```

#### Update

```python
# Update specific rows
db.update(
    "products",
    data={"stock": 45},
    where={"id": 1}
)

# Update all rows
db.update(
    "products",
    data={"stock": 0},
    update_all=True
)
```

#### Delete

```python
# Delete specific rows
db.delete("products", where={"id": 1})

# Delete all rows
db.delete("products", delete_all=True)
```

### Advanced Features

#### Lambda Filters

```python
# Filter with custom lambda function
expensive_products = db.select(
    from_table="products",
    filter=lambda price: price > 500
)
```

#### Regular Expression Matching

```python
# Match with regex patterns
tech_products = db.select(
    from_table="products",
    regexp={"name": [r"Laptop", r"Phone", r"Tablet"]}
)
```

#### Response Formatters

```python
# Get as JSON
json_data = db.select(from_table="products", as_json=True)

# Get as Pandas DataFrame
df = db.select(from_table="products", as_dataframe=True)

# Get as Pydantic models
products = db.select(
    from_table="products",
    model=Product,
    as_model=True
)
# Returns: list[Product]
```

#### Unique Constraints

```python
from mentodb import UniqueMatch

class User(BaseModel):
    id: int
    username: str
    email: str
    unique_check: UniqueMatch("username", "email")

# Insert will check uniqueness
db.insert("users", data={...}, check_model=User)
```

### Connection Management

```python
# Manual connection management
conn = MentoConnection("mydb.db", timeout=10.0)
db = Mento(conn)
# ... do work ...
conn.close()

# With context manager (recommended)
with MentoConnection("mydb.db") as conn:
    db = Mento(conn)
    # Automatic commit on success, rollback on exception
```

## 🔄 Migration from v1.x

MentoDB 2.0 includes breaking changes. See [MIGRATION.md](MIGRATION.md) for detailed upgrade instructions.

### Key Changes

| v1.x | v2.0 |
|------|------|
| Python 3.9.6+ | Python 3.12+ |
| Pydantic v1 | Pydantic v2 |
| String formatting in SQL | Parameterized queries |
| NumPy dependency | No NumPy (uses `collections.abc`) |
| `BaseException` | `ValueError` for validation |
| Manual transaction handling | Context managers |

### Quick Migration Example

**Before (v1.x):**
```python
from mentodb import Mento, MentoConnection

conn = MentoConnection("db.sqlite")
db = Mento(conn)
# ... operations ...
conn.close()
```

**After (v2.0):**
```python
from mentodb import Mento, MentoConnection

with MentoConnection("db.sqlite") as conn:
    db = Mento(conn)
    # ... operations ...
    # Auto-commit/rollback
```

## 🧪 Development

### Setup

```bash
git clone https://github.com/fswair/MentoDB.git
cd MentoDB
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=mentodb --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type checking
mypy .
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Pydantic](https://docs.pydantic.dev/)
- Inspired by modern ORM design patterns
- Created and maintained by [@fswair](https://github.com/fswair)

## 📊 Project Stats

- ⭐ Star this repo if you find it useful!
- 🐛 [Report bugs](https://github.com/fswair/MentoDB/issues)
- 💡 [Request features](https://github.com/fswair/MentoDB/issues)
- 📖 [Read the docs](https://github.com/fswair/MentoDB#readme)

---

**Note:** This is version 2.0 with breaking changes from 1.x. See [CHANGELOG.md](CHANGELOG.md) for details.
