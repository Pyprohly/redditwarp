
from typing import ClassVar
from dataclasses import dataclass
from pprint import pformat

class APIError(Exception):
	"""A base exception class denoting that something in the response body
	from an API request is amiss. Either an error was indicated by the API
	or the structure is of something the client isn't prepared to handle.
	"""

	def __init__(self, response: 'Optional[Response]'):
		super().__init__()
		self.response = response

class BadJSONLayout(APIError):
	"""The response body contains JSON data that the client can't handle."""

	def __init__(self, response, json=None):
		super().__init__(response)
		self.json = json

	def __str__(self):
		return f'\\\n{pformat(self.json)}\n\n' \
				'** Please file a bug report with RedditWrap! **\n'

class RedditAPIError(APIError):
	"""An error class denoting an error that was indicated in the
	response body of an API request, occurring when the remote API
	wishes to inform the client that a service request was carried
	out unsuccessfully.
	"""

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
		err_names = [err.name for err in self.errors]
		return f'<{self.__class__.__name__} ({self.response.status}) {err_names}>'

	def __str__(self):
		err_count = len(self.errors)
		if err_count > 1:
			return f'multiple errors ({err_count}) encountered:\n' \
					+ '\n'.join(
						f"  {err.name}: {err.message}{err.field and ' -> '}{err.field}"
						for err in self.errors)

		return f"{self.name}: {self.message}{self.field and ' -> '}{self.field}"

class ContentCreationCooldown(RedditAPIError):
	"""Used over RedditAPIError when the error items list contains
	a RATELIMIT error, and it is the only error in the list.
	"""

	def __str__(self):
		return super().__str__() + '''

Looks like you hit a content creation ratelimit. This can happen when
your account has low karma or no verified email.
'''

@dataclass
class RedditErrorItem:
	NAME: ClassVar[str] = ''
	name: str
	message: str
	field: str

def parse_reddit_error_items(data):
	errors = data.get('json', {}).get('errors')
	if errors:
		l = []
		for e in errors:
			name, message, field = e
			l.append(RedditErrorItem(name, message, field or ''))
		return l
	return None

def new_reddit_api_error(response, error_list):
	cls = RedditAPIError
	if (len(error_list) == 1) and (error_list[0].name == 'RATELIMIT'):
		cls = ContentCreationCooldown
	return cls(response, error_list)
