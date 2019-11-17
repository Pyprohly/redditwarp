"""Interfaces for credentials."""

import abc
import datetime

class BaseCredentials(abc.ABC):
	"""Base class for all credentials.

	Attributes
	----------
	token: :class:`str`
		The bearer token that can be used in HTTP headers to make
		authenticated requests.
	expiry: Optional[:class:`datetime`]
		When the token expires and is no longer valid.
		If ``None``, the token is assumed to never expire.
	"""

	def __init__(self, *, token=None, expiry=None):
		self.token = token
		self.expiry = expiry

	def expired(self):
		""":class:`bool`: ``True`` if the token is expired."""
		if self.expiry is None:
			return False
		return datetime.datetime.utcnow() >= self.expiry

	def valid(self):
		""":class:`bool`: ``True`` if the token is set and isn't expired."""
		return (self.token is not None) and (not self.expired())

class Credentials(BaseCredentials, abc.ABC):
	@abc.abstractmethod
	def refresh(self, requestor):
		raise NotImplementedError

	@abc.abstractmethod
	def prepare_requestor(self, requestor):
		raise NotImplementedError

	'''
	def apply(self, headers):
		headers['Authorization'] = f'Bearer {self.token}'

	def before_request(self, request, method, url, headers):
		if not self.valid:
			self.refresh(request)
		self.apply(headers)
	'''
