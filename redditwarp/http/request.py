
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional
    from collections.abc import MutableMapping
    from .payload import Payload

from dataclasses import dataclass, field

from .util.join_params_ import join_params

@dataclass(eq=False)
class Request:
    verb: str
    uri: str
    params: MutableMapping[str, Optional[str]] = field(default_factory=dict)
    payload: Optional[Payload] = None
    headers: MutableMapping[str, str] = field(default_factory=dict)

    def get_url(self) -> str:
        return join_params(self.uri, self.params)
