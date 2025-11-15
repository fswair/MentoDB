r"""
MentoDB - A modern SQLite ORM for Python

Author: @fswair
Version: 2.1
Structure: SQLITE3

New in 2.1:
- Async support (AsyncMentoConnection)
- Query Builder with fluent API
- Database migrations
- Connection pooling
- Relationships and foreign keys
- Index management
- Bulk operations
- Query result caching
"""

# Core components
from .utils import (
    Mento,
    PrimaryKey,
    Column,
    Fetch,
    UniqueMatch,
    MentoExceptions,
    Static,
    AutoResponse,
)
from .connection import MentoConnection
from .models import DefaultModel

# Async support
from .async_connection import AsyncMentoConnection

# Query building
from .query_builder import QueryBuilder

# Database management
from .migrations import Migration, MigrationManager
from .indexes import IndexManager
from .relationships import (
    RelationshipManager,
    ForeignKey,
    RelationType,
    OnAction,
)

# Performance features
from .connection_pool import ConnectionPool
from .bulk_operations import BulkOperations
from .cache import QueryCache, CachedConnection

# External dependencies
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from typing import TypeVar

__version__ = "2.1"
__all__ = [
    # Core
    "Mento",
    "MentoConnection",
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
    "AsyncMentoConnection",
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
]
