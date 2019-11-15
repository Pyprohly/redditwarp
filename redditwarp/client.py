
from .http import HTTPClient


class Client:
	def __init__(self):
		self.http = HTTPClient()

	def request(self, method, url, *args):
		return self.http.request(method, url, *args)


