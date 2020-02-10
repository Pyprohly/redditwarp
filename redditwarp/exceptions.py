
from typing import ClassVar
from dataclasses import dataclass


class ClientError:
	...



class APIError(Exception):
	"""A base exception class representing an error that was indicated
	in the response body, occurring when the remote API wishes to inform
	the client that a service request was unsuccessful.
	"""

	def __init__(self, response):
		super().__init__()
		self.response = response

class RedditAPIError(APIError):
	@property
	def name(self):
		return self.errors[0].name

	@property
	def message(self):
		return self.errors[0].message

	@property
	def field(self):
		return self.errors[0].field

	def __init__(self, response, errors):
		"""
		Parameters
		----------
		response: :class:`.http.Response`
		errors: List[:class:`.RedditErrorItem`]
		"""
		super().__init__(response)
		errors[0]
		self.errors = errors

	def __repr__(self):
		return f'{self.__class__.__name__}(%r)' % self.__str__()

	def __str__(self):
		return f'{self.name}: {self.message}'

class ContentCreationCooldown(RedditAPIError):
	"""Used over RedditAPIError when the error items list contains
	a RATELIMIT error, and it is the only error in the list.
	"""

@dataclass
class RedditErrorItem:
	NAME: ClassVar[str] = ''
	name: str
	message: str
	field: str
