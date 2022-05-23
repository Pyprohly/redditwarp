
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from ..models.user_ASYNC import User, SuspendedUser


def load_user(d: Mapping[str, Any], client: Client) -> User:
    return User(d, client)

def load_potentially_suspended_user(d: Mapping[str, Any], client: Client) -> object:
    if d.get('is_suspended', False):
        return SuspendedUser(d, client)
    return User(d, client)
