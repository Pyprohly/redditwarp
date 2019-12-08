
from .http import HTTPClient

class Client:
	def __init__(self):
		self.http = HTTPClient()

	def request(self, verb, path, *, params=None, data=None, headers=None):
		return self.http.request(verb, path, params=params, data=data, headers=headers)
