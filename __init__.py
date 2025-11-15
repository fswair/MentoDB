r"""
MentoDB - A modern SQLite ORM for Python

Author: @fswair
Version: 2.0
Structure: SQLITE3
"""

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
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from typing import TypeVar

__version__ = "2.0"
__all__ = [
    "Mento",
    "PrimaryKey",
    "Column",
    "Fetch",
    "UniqueMatch",
    "MentoExceptions",
    "Static",
    "AutoResponse",
    "MentoConnection",
    "DefaultModel",
    "BaseModel",
]
