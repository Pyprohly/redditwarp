
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ...models.user_SYNC import User

def load_user(d: Mapping[str, Any], client: Client) -> User:
    return User(d, client)
