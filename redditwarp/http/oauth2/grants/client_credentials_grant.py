
from . import Grant

class ClientCredentialsGrant(Grant):
	"""
	Parameters
	----------
	client: :class:`.Client`
	scopes: Sequence[str]
	"""

	grant_type = 'client_credentials'

	def __init__(self, client, scopes):
		super().__init__(client)
		self.scopes = scopes

	def scope_string(self):
		return ' '.join(self.scopes)

	def retrieve_token(self):
		""":class:`.Token`"""
		...
