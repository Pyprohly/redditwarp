
from .transport.requests import AuthenticatedSession


class Route:
	BASE = 'https://oauth.reddit.com'

	def __init__(self, verb, path, **parameters):
		self.verb = verb
		self.path = path
		self.url = self.BASE + path

class HTTPClient:
	def __init__(self):
		self.session = AuthenticatedSession()

	def request(self, verb, url, *args):
		return self.session.request(verb, url, *args)
