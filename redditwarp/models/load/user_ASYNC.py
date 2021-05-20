
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ..user_ASYNC import User

def load_user(d: Mapping[str, Any], client: Client) -> User:
    return User(d, client)
