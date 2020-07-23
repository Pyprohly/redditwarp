
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_sync import Client

from .submission_sync import Submission

class SiteProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.submission = Submission(client)
