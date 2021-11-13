
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ..user_base import BaseUser

from ..user_SYNC import User


def promote_from_base(base_user: BaseUser, client: Client) -> User:
    return User(base_user.d, client)


def load_user(d: Mapping[str, Any], client: Client) -> User:
    return User(d, client)
