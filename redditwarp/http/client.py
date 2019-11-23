
from .transport import Request
from .transport.requests import AuthorizedSession


class HTTPClient:
	AUTHORIZATION_URL = 'https://www.reddit.com'
	NO_AUTH_RESOURCE_URL = 'https://www.reddit.com'
	RESOURCE_URL = 'https://oauth.reddit.com'

	def __init__(self):
		self.session: 'Requestor' = AuthorizedSession()
		self.base_url = self.RESOURCE_URL

	def request(self, verb, path):
		url = self.base_url + path
		req = Request(verb, url)
		return self.session.request(req)
