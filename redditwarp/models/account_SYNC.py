
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from .account_base import (
    MyAccountMixinBase,
)

class MyAccount(MyAccountMixinBase):
    def __init__(self, d: Mapping[str, Any], client: Client):
        super().__init__(d)
        self.client = client
