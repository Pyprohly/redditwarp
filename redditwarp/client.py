
from .http import HTTPClient


class Client:
	def __init__(self):
		self.http = HTTPClient()

	def request(self, verb, path):
		return self.http.request(verb, path)
