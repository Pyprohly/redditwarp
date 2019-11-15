
from .transport.requests import AuthenticatedSession


class HTTPClient:
	def __init__(self):
		self.session = AuthenticatedSession()

	def request(self):
		