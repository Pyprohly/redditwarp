
from typing import ClassVar
from dataclasses import dataclass

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

	def __str__(self):
		return super().__str__() + '''

Looks like you hit a content creation ratelimit. This API error can happen
when your account has low karma or no verified email.
'''

@dataclass
class RedditErrorItem:
	NAME: ClassVar[str] = ''
	name: str
	message: str
	field: str

def parse_reddit_error_items(d):
	errors = d.get('json', {}).get('errors')
	if errors:
		return [RedditErrorItem(*e) for e in errors]
	return None

def new_reddit_api_error(response, error_list):
	cls = RedditAPIError
	if (len(error_list) == 1) and (error_list[0].name == 'RATELIMIT'):
		cls = ContentCreationCooldown
	return cls(response, error_list)
