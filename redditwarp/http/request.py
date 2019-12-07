
class Request:
	"""An ABC that stores info about an outgoing request."""

	def __init__(self, verb, url, params, data=None, headers=None):
		r"""
		Parameters
		----------
		verb: str
			The HTTP method to use for the request.
		url: str
			The URL to be requested.
		params: Optional[Dict[str, str]]
			Query parameters appended to the URL.
		data: Optional[:class:`.Payload`]
			The body/payload of the HTTP request.
		headers: Optional[Mapping[str, str]]
			Request headers.
		"""
		self.verb = verb
		self.url = url
		self.params = params
		self.data = data
		self.headers = {} if headers is None else headers

	def __repr__(self):
		attrs = (
			('verb', self.verb),
			('url', self.url),
			('params', self.params),
			('data', self.data),
			('headers', self.headers)
		)
		return '%s(%s%s)' % (
				type(self).__name__,
				', '.join('%s=%r' % t for t in attrs),
				f', **{self.kwargs}' if self.kwargs else '')

	def __member_keys(self):
		return ('verb', 'url', 'params', 'data', 'headers')
	def __member_values(self):
		return (self.verb, self.url, self.params, self.data, self.headers)
	def __member_items(self):
		return zip(self.__member_keys(), self.__member_values())
