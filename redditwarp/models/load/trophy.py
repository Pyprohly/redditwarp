
from __future__ import annotations
from typing import Any, Mapping

from ..trophy import Trophy

def load_trophy(d: Mapping[str, Any]) -> Trophy:
    return Trophy(
        d=d,
        name=d['name'],
        description=d['description'] or '',
        icon_40=d['icon_40'],
        icon_70=d['icon_70'],
    )
