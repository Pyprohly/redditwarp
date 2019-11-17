
from .transport.requests import AuthorizedSession


class Route:
	# Auth base
	BASE = 'https://oauth.reddit.com'
	# Non auth base??

	def __init__(self, verb, path, **parameters):
		self.verb = verb
		self.path = path
		self.url = self.BASE + path

class HTTPClient:
	AUTHORIZATION_URL = 'https://www.reddit.com'
	NO_AUTH_RESOURCE_URL = 'https://www.reddit.com'
	RESOURCE_URL = 'https://oauth.reddit.com'

	def __init__(self):
		self.session: 'Requestor' = AuthorizedSession()
		self.base_url = self.RESOURCE_URL

	def request(self, verb, path, *args):
		url = self.base_url + path
		return self.session.request(verb, url, *args)
