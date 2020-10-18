
from __future__ import annotations
from typing import Any, Mapping

from ...models.partial_user import PartialUser

def load_partial_user(d: Mapping[str, Any], id36: str) -> PartialUser:
    return PartialUser(d, id36)
