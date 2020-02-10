
class Request:
	"""An ABC that stores info about an outgoing request."""

	def __init__(self, verb, url, params=None, payload=None, headers=None):
		r"""
		Parameters
		----------
		verb: str
			The HTTP method to use for the request.
		url: str
			The URL to be requested.
		params: Optional[Mapping[str, str]]
			Query parameters appended to the URL.
		payload: Optional[:class:`.Payload`]
			The body/payload of the HTTP request.
		headers: Optional[Mapping[str, str]]
			Request headers.
		"""
		self.verb = verb
		self.url = url
		self.params = {} if params is None else params
		self.payload = payload
		self.headers = {} if headers is None else headers

	def __repr__(self):
		attrs = (
			('verb', self.verb),
			('url', self.url),
			('params', self.params),
			('payload', self.payload),
			('headers', self.headers)
		)
		return '%s(%s)' % (
				type(self).__name__,
				', '.join('%s=%r' % t for t in attrs))

	def __member_keys(self):
		return ('verb', 'url', 'params', 'payload', 'headers')
	def __member_values(self):
		return (self.verb, self.url, self.params, self.payload, self.headers)
	def __member_items(self):
		return zip(self.__member_keys(), self.__member_values())
