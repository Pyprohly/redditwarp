
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from .requisition import Requisition
    from .request import Request
    from .response import Response

from dataclasses import dataclass


@dataclass(repr=False, eq=False)
class Exchange:
    requisition: Requisition
    request: Request
    response: Response
    history: Sequence[Response]
