
from __future__ import annotations
from typing import Mapping

import uuid

from ..auth.grants import InstalledClientGrant

_REDDITWARP_CLIENT_ID: str = 'Jirijsc5rRo79AzJBUttyQ'

def get_redditwarp_client_id() -> str:
    return _REDDITWARP_CLIENT_ID

def get_installed_client_grant() -> Mapping[str, str]:
    return InstalledClientGrant(str(uuid.uuid1()))
