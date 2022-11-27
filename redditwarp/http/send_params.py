
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .requisition import Requisition

from dataclasses import dataclass


@dataclass(repr=False, eq=False)
class SendParams:
    requisition: Requisition
    timeout: float = -2
    follow_redirects: Optional[bool] = None
