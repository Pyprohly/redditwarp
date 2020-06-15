
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ...client_sync import Client

from .submission.submission_sync import submission
from .submissions.submissions_sync import submissions

class fetch:
	def __init__(self, client: Client):
		self._client = client
		self.submission = submission(client)
		self.submissions = submissions(client)
