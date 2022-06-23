from .utils import Mento, PrimaryKey, Column, Fetch, UniqueMatch
from .connection import MentoConnection
from .models import DefaultModel
from pydantic import BaseModel
from numpy import iterable
from typing import TypeVar


mento: Mento = Mento()


"""
Author: @fswair
Version: 1.1
Structure: SQLITE3
"""