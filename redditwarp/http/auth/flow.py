
class GrantTokenExchanger:
	def __init__(self, grant):
		self.grant = grant

	def retrieve_token(self):
		...

	def retrieve_access_token(self):
		return self.retrieve_token().access_token



class AuthorizationCodeFlowStage:
	...

class AuthorizationCodeRequest(AuthorizationCodeFlowStage):
	...









class AuthorizationFlow:
	"""An OAuth flow is a process of obtaining an access token."""

	def __init__(self, provider):
		self.provider = provider

	def retrieve_token(self):
		raise NotImplementedError


class AuthorizationCodeFlow(AuthorizationFlow):
	grant_type = 'code'

	def __init__(self, provider, grant):
		super().__init__(provider)

	def authorization_url(self):
		...

	def retrieve_token(self):
		...

class ClientCredentialsFlow(AuthorizationFlow):
	grant_type = 'client_credentials'

	def __init__(self, provider, grant):
		super().__init__(provider)

	def retrieve_token(self):
		...
