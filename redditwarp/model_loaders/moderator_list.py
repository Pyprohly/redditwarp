
from __future__ import annotations
from typing import Any, Mapping

from ..models.moderator_list import ModeratorListItem

def load_moderator_list_item(d: Mapping[str, Any]) -> ModeratorListItem:
    return ModeratorListItem(d)
