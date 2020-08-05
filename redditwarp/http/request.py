
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional
    from collections.abc import MutableMapping
    from .payload import Payload

from dataclasses import dataclass, field

@dataclass(eq=False)
class Request:
    verb: str
    uri: str
    params: MutableMapping[str, Optional[str]] = field(default_factory=dict)
    payload: Optional[Payload] = None
    headers: MutableMapping[str, str] = field(default_factory=dict)
