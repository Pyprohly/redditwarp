
from .submission import submission

class fetch:
	def __init__(self, client):
		self._client = client
		self.submission = submission(client)
