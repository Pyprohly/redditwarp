
from __future__ import annotations
from typing import Optional, ClassVar

from dataclasses import dataclass

from ...auth.grants import AuthorizationGrant

@dataclass(frozen=True)
class InstalledClientGrant(AuthorizationGrant):
    GRANT_TYPE: ClassVar[str] = "https://oauth.reddit.com/grants/installed_client"
    device_id: str
    scope: Optional[str] = None
