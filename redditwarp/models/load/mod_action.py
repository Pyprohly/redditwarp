
from __future__ import annotations
from typing import Any, Mapping

from ..mod_action import ModAction

def load_mod_action(d: Mapping[str, Any]) -> ModAction:
    return ModAction(d)
