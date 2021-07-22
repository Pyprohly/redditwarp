
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .mixins.account import (
    MyAccount as MyAccountMixin,
)

class MyAccount(MyAccountMixin):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client
