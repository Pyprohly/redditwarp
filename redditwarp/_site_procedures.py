
from .models.submission import fetch_submission

class Fetch:
	def __init__(self, client):
		self.client = client
		self.submission = fetch_submission(client)

class SiteProcedures:
	def __init__(self, client):
		self.client = client
		self.fetch = Fetch(client)
