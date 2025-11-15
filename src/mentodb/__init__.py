r"""
MentoDB - A modern SQLite ORM for Python

Author: @fswair
Version: 2.1
Structure: SQLITE3

New in 2.1:
- Async support (AsyncConnection)
- Query Builder with fluent API
- Database migrations
- Connection pooling
- Relationships and foreign keys
- Index management
- Bulk operations
- Query result caching
"""

# Core components
from .core import (
    Mento,
    Connection,
    PrimaryKey,
    Column,
    Fetch,
    UniqueMatch,
    MentoExceptions,
    Static,
    AutoResponse,
    DefaultModel,
)

# Async support
from .async_api import AsyncConnection

# Query building
from .query import QueryBuilder

# Database management
from .migrations import Migration, MigrationManager
from .schema import (
    IndexManager,
    RelationshipManager,
    ForeignKey,
    RelationType,
    OnAction,
)

# Performance features
from .performance import (
    ConnectionPool,
    BulkOperations,
    QueryCache,
    CachedConnection,
)

# External dependencies
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from typing import TypeVar

# Backward compatibility aliases (deprecated, will be removed in v3.0)
MentoConnection = Connection
AsyncMentoConnection = AsyncConnection

__version__ = "2.1.2"
__all__ = [
    # Core (new clean names)
    "Mento",
    "Connection",
    "PrimaryKey",
    "Column",
    "Fetch",
    "UniqueMatch",
    "MentoExceptions",
    "Static",
    "AutoResponse",
    "DefaultModel",
    "BaseModel",
    # Async
    "AsyncConnection",
    # Query building
    "QueryBuilder",
    # Database management
    "Migration",
    "MigrationManager",
    "IndexManager",
    "RelationshipManager",
    "ForeignKey",
    # Performance
    "ConnectionPool",
    "BulkOperations",
    "QueryCache",
    "CachedConnection",
    # Deprecated (backward compatibility)
    "MentoConnection",  # Use Connection instead
    "AsyncMentoConnection",  # Use AsyncConnection instead
]
