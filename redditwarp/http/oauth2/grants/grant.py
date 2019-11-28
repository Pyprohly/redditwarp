

class Automatic:
	pass

class Interactive:
	pass

class ScopesMixin:
	...
	def scope_string(self):
		return ' '.join(self.scopes)

class Grant:
	def __init__(self, client):
		self.client = client

	def retrieve_token(self):
		raise NotImplementedError
