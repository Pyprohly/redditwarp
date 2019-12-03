
from .. import AuthorizationGrant
from .. import AuthorizationFlow

class AuthorizationCodeGrant(AuthorizationGrant):
	def __init__(self, client_id, client_secret, redirect_uri, scope='', state=None, code=None, extra_parameters=None):
		super().__init__(client_id, client_secret)
		self.redirect_uri = redirect_uri
		self.scope = scope
		self.state = state
		self.code = code
		self.extra_parameters = extra_parameters

class AuthorizationCodeFlow(AuthorizationFlow):
	response_type = 'code'
	grant_type = 'refresh_token'

	def __init__(self, provider, grant):
		super().__init__(provider)
		self.grant = grant

	def authorization_url(self):
		...

	def retrieve_token(self):
		...



