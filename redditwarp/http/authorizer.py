
class Authorizer:
	"""Knows how to authorize requests."""

	@property
	def access_token(self):
		return self.token.access_token

	def __init__(self, token_client):
		self.token_client = token_client
		self.token = None

	def prepare_request(request) -> None:
		request.headers['Authorization'] = '%s %s' % (self.token.token_type, self.access_token)

	def fetch_token(self):
		token_response = self.token_client.retrieve_token()
