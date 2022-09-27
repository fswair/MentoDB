r"""
Author: @fswair
Version: 1.2
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
from numpy import iterable
from typing import TypeVar, AnyStr
