
from __future__ import annotations

import sys

from .. import __about__
from ..http.transport.reg_ASYNC import load_transport, transport_registry

def get_user_agent() -> str:
    tt = load_transport()
    return ' '.join([
        f"{__about__.__title__}/{__about__.__version__}",
        f"Python/{sys.version.split(None, 1)[0]}",
        f"{tt.name}/{tt.version}",
    ])

def get_user_agent_from_session(session: object) -> str:
    tokens = [
        f"{__about__.__title__}/{__about__.__version__}",
        f"Python/{sys.version.split(None, 1)[0]}",
    ]
    if session:
        tt = transport_registry.get(session.__module__)
        if tt:
            tokens.append(f"{tt.name}/{tt.version}")
    return ' '.join(tokens)
