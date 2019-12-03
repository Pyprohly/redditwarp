
from .. import AuthorizationGrant
from .. import AuthorizationFlow

class RefreshTokenGrant(AuthorizationGrant):
	def __init__(self, client_id, client_secret, refresh_token, scope=''):
		super().__init__(client_id, client_secret)
		self.refresh_token = refresh_token
		self.scope = scope # _scope.scope_string(scope)

class RefreshTokenFlow(AuthorizationFlow):
	grant_type = 'refresh_token'

	def __init__(self, provider, grant):
		super().__init__(provider)

	def retrieve_token(self):
		...
