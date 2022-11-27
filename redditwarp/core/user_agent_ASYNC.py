
from __future__ import annotations

import sys

from .. import __about__
from ..http.transport.reg_ASYNC import transport_registry

def get_user_agent(*, module_member: object = None) -> str:
    parts = [
        f"{__about__.__title__}/{__about__.__version__}",
        f"Python/{sys.version.split(None, 1)[0]}",
    ]
    if module_member is not None:
        ti = transport_registry.get(module_member.__module__)
        if ti is not None:
            parts.append(f"{ti.name}/{ti.version}")
    return ' '.join(parts)
