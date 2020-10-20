
from __future__ import annotations
from typing import Any, Mapping

from ...models.trophy import Trophy

def load_trophy(d: Mapping[str, Any]) -> Trophy:
    return Trophy(d)
