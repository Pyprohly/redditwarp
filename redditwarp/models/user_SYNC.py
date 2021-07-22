
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .mixins.user import (
    User as UserMixin,
)

class User(UserMixin):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client
