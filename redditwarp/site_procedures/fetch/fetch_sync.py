
from .submission import submission
from .submissions import submissions

class fetch:
	def __init__(self, client):
		self._client = client
		self.submission = submission(client)
		self.submissions = submissions(client)
