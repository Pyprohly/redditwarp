
from .transport import Request
from .transport.requests import AuthorizedSession


class HTTPClient:
	AUTHORIZATION_URL = 'https://www.reddit.com'
	NO_AUTH_RESOURCE_URL = 'https://www.reddit.com'
	RESOURCE_URL = 'https://oauth.reddit.com'

	def __init__(self):
		"""
		Attributes
		----------
		session: :class:`~.Requestor`
		"""
		self.session = Ratelimited(Retryable(Session()))
		self.auth_session = Authorized(self.session)

		self.url_base = self.RESOURCE_URL

	def request(self, verb, path):
		url = self.url_base + path
		req = Request(verb, url)
		return self.session.request(req)
