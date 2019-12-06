
TIMEOUT = 8

class Requestor(abc.ABC):
	"""Interface. A Requestor is a thing that makes requests."""

	@abc.abstractmethod
	def request(self, request, timeout=None):
		r"""Make an HTTP request.

		Parameters
		----------
		request: :class:`Request`
			The URL to be requested.
		timeout: Optional[:class:`int`]
			The number of seconds to wait for a response from the server.
			If ``None``, the transport default timeout will be used.

		Returns
		-------
		:class:`Response`
			The HTTP response.

		Raises
		------
		:class:`warp.http.auth.exceptions.TransportError`
			If any exception occurred.
		"""
		raise NotImplementedError

class RequestorDecorator(Requestor):
	def __init__(self, requestor):
		self.requestor = requestor

	def request(self, request, **kwargs):
		return self.requestor.request(request, **kwargs)


class Authorized(RequestorDecorator):
	"""A Requests Session wrapper class that holds credentials.

	This class is used to perform requests to API endpoints that require
	authorization. The :meth:`request` method handles adding authorization
	headers to the request and refreshing credentials when needed.

	Parameters
	----------
	credentials: :class:`warp.http.auth.credentials.Credentials`
		The credentials to apply to requests.
	requestor: Optional[:class:`~.Requestor`]
		The requestor used when making API requests.
	token_requestor: Optional[:class:`~.Requestor`]
		The requestor used for refreshing credentials.
	"""

	def __init__(self, requestor, token_client):
		super().__init__(requestor)
		self.token_client = token_client

	def request(self, request, timeout=TIMEOUT):
		self.prepare_request(request)
		resp = self.requestor.request(request)
		return resp


		return
		if not self.credentials.valid():
			self.credentials.refresh(self._token_requestor)

		self.credentials.prepare_requestor(self._requestor)
		request = partial(self.credentials.prepare_requestor(self._requestor),
				url=url, verb=verb, data=data, headers=headers, **kwargs)

		response = request()
		if response.status == 401:
			'''
			log.info(
				'Refreshing credentials due to a %s response. Attempt %s/%s.',
				response.status_code, _credential_refresh_attempt + 1,
				self._max_refresh_attempts)
			'''
			# Even though we check the credentials before making the request,
			# the token could have expired in the time between the check and
			# the request. Check that the response code is not 401.
			self.credentials.refresh(self._token_requestor)
			response = request()

		return response

	def prepare_request(self, request):
		

