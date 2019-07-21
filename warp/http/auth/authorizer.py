
import abc

class BaseAuthorizer(abc.ABC):
	@abc.abstractmethod
	def prepare_request(self):
		...

class NoAuthAuthorizer(BaseAuthorizer):
	...

class Authorizer(BaseAuthorizer):
	def __init__(self, access_token):
		self.access_token = access_token

class OAuth2Authorizer(Authorizer):
	authorization_url = 'https://www.reddit.com'
	resource_url = 'https://oauth.reddit.com'

	def __init__(self, client_id, client_secret, access_token=None):
		super().__init__(access_token=access_token)
		self.client_id = client_id
		self.client_secret = client_secret

class ScriptAuthorizer(OAuth2Authorizer):
	def __init__(self, client_id, client_secret, username, password):
		super().__init__(client_id=client_id, client_secret=client_secret)
		self.username = username
		self.password = password

	def refresh(self):
		pass

class WebAuthorizer(OAuth2Authorizer):
	def authorization_url(self):
		...
