
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ..user_base import BaseUser

from ..user_ASYNC import User


def promote_base_user(base: BaseUser, client: Client) -> User:
    return User(base.d, client)


def load_user(d: Mapping[str, Any], client: Client) -> User:
    return User(d, client)
