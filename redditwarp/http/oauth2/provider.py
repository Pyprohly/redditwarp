
class Provider:
	def __init__(self, auth_endpoint, token_endpoint, resource_base_url):
		self.auth_endpoint = auth_endpoint
		self.token_endpoint = token_endpoint
		self.resource_base_url = resource_base_url

	def authorization_url(self):
		...
