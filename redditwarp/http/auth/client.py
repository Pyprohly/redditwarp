
from ..transport import Request

class TokenClient:
	"""The token client will exchange an authorisation grant
	for an OAuth2 token.
	"""
	def __init__(self, requestor, provider, client_credentials, grant):
		self.requestor = requestor
		self.provider = provider
		self.client_credentials = client_credentials
		self.grant = grant

	def retrieve_token():
		raise NotImplementedError

class AuthorizationCodeClient(TokenClient):
	def retrieve_token():
		...


class ImplicitClient(TokenClient):
	def retrieve_token():
		...

class ResourceOwnerPasswordCredentialsClient(TokenClient):
	def retrieve_token():
		...

class ClientCredentialsClient(TokenClient):
	def retrieve_token():

		req = Request('POST', self.provider.token_endpoint, )
