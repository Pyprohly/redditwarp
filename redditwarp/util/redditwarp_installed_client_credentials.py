
from __future__ import annotations

import uuid


_REDDITWARP_CLIENT_ID: str = 'Jirijsc5rRo79AzJBUttyQ'

def get_redditwarp_client_id() -> str:
    return _REDDITWARP_CLIENT_ID


_device_id: str = ''

def get_device_id() -> str:
    global _device_id
    if not _device_id:
        _device_id = str(uuid.uuid1())
    return _device_id
