
from .fetch import fetch

class SiteProcedures:
	def __init__(self, client):
		self._client = client
		self.fetch = fetch(client)
