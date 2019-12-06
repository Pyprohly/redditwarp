
from .transport import Request
from .transport.requests import AuthorizedSession


class HTTPClient:
	AUTHORIZATION_URL = 'https://www.reddit.com/api/v1/authorize'
	TOKEN_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
	RESOURCE_BASE_URL = 'https://oauth.reddit.com'
	NO_AUTH_RESOURCE_BASE_URL = 'https://www.reddit.com'

	def __init__(self):
		"""
		Attributes
		----------
		session: :class:`~.Requestor`
		"""
		#self.session = Ratelimited(Retryable(Session()))

		self.url_base = self.RESOURCE_BASE_URL

		self._token_requestor = Session()
		session = Session()
		provider = Provider(AUTHORIZATION_URL, TOKEN_ENDPOINT, RESOURCE_BASE_URL)
		client_credentials = ClientCredentials('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE')
		grant = ClientCredentialsGrant()
		token_client = ClientCredentialsClient(self._token_requestor, provider, client_credentials, grant)
		authorized_session = Authorized(session, token_client)
		self.session = authorized_session

	def request(self, verb, path):
		url = self.url_base + path
		req = Request(verb, url)
		return self.session.request(req)
