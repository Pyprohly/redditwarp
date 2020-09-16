
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client

from .submission_SYNC import Submission
from .subreddit_SYNC import Subreddit

class SiteProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.submission = Submission(client)
        self.subreddit = Subreddit(client)
