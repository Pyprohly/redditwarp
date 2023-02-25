
from __future__ import annotations
from typing import Any, Mapping

from dataclasses import dataclass

from .datamemento import DatamementoDataclassesMixin

@dataclass(repr=False, eq=False)
class Trophy(DatamementoDataclassesMixin):
    d: Mapping[str, Any]
    name: str
    ("""
        E.g., `Three-Year Club`.
        """)
    description: str
    icon_40: str
    ("""
        The URL of a 41x41 px icon for the trophy.

        E.g., `https://www.redditstatic.com/awards2/3_year_club-40.png`.
        """)
    icon_70: str
    ("""
        The URL of a 71x71 px icon for the trophy.

        E.g., `https://www.redditstatic.com/awards2/3_year_club-70.png`.
        """)
