
from __future__ import annotations
from typing import Any, Mapping

from ..models.user_summary import UserSummary

def load_user_summary(d: Mapping[str, Any], id36: str) -> UserSummary:
    return UserSummary(d, id36)
