
from . import Grant

class RefreshTokenGrant(Grant):
	"""
	Parameters
	----------
	client: :class:`.Client`
	scopes: Sequence[str]
	"""

	grant_type = 'refresh_token'

	def __init__(self, client, scopes):
		super().__init__(client)
		self.scopes = scopes

	def scope_string(self):
		return ' '.join(self.scopes)

	def retrieve_token(self):
		""":class:`.Token`"""
		...
