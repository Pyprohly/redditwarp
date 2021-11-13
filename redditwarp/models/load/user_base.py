
from __future__ import annotations
from typing import Any, Mapping

from ..user_base import BaseUser

def load_base_user(d: Mapping[str, Any]) -> BaseUser:
    return BaseUser(d)
