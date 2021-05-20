
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ..account_ASYNC import MyAccount

def load_account(d: Mapping[str, Any], client: Client) -> MyAccount:
    return MyAccount(d, client)
