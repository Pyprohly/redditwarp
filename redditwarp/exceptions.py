
from dataclasses import dataclass
from pprint import pformat

from .http import exceptions as http_exc

class APIError(http_exc.ResponseException):
	"""A base exception class denoting that something in the response body
	from an API request is amiss. Either an error was indicated by the API
	or the structure is of something the client isn't prepared to handle.
	"""

class HTTPStatusError(http_exc.StatusCodeException):
	"""There was nothing useful to process in the response body and the
	response had a bad status code.
	"""



class ResponseContentError(APIError):
	pass

class UnidentifiedResponseContentError(ResponseContentError):
	"""The response body contains data that the client isn't prepared to handle."""

	def __str__(self):
		return '\\\n\n** Please file a bug report with RedditWrap! **'

class UnidentifiedJSONLayoutResponseContentError(UnidentifiedResponseContentError):
	# Unused
	"""The response body contains JSON data that the client isn't prepared to handle."""

	def __init__(self, response, json):
		super().__init__(response)
		self.json = json

	def __str__(self):
		return f'\\\n{pformat(self.json)}\n\n' \
				'** Please file a bug report with RedditWrap! **'

class UnacceptableResponseContentError(ResponseContentError):
	"""The response body contains data in a format that the client doesn’t want
	to or can't handle.
	"""

	def __str__(self):
		return f'\\\n{self.response.data}\n\n' \
				'** Please file a bug report with RedditWrap! **'

class HTMLDocumentResponseContentError(ResponseContentError):
	pass

class UserAgentRequired(HTMLDocumentResponseContentError):
	pass


def get_response_content_error(resp):
	if resp.data.lower().startswith(b'<!doctype html>'):
		if b'>user agent required</' in resp.data:
			return UserAgentRequired(resp)
		return HTMLDocumentResponseContentError(resp)
	return UnidentifiedResponseContentError(resp)

def raise_for_json_response_content_error(resp, json_data):
	if {'jquery', 'success'} <= json_data.keys():
		raise UnacceptableResponseContentError(resp)



class RedditAPIError(APIError):
	"""An error class denoting an error that was indicated in the
	response body of an API request, occurring when the remote API
	wishes to inform the client that a service request was carried
	out unsuccessfully.
	"""

	@property
	def codename(self):
		return ''

	@property
	def detail(self):
		return ''

	@property
	def field(self):
		return ''

	def __repr__(self):
		return f'<{self.__class__.__name__} ({self.response})>'

	def __str__(self):
		return f"{self.codename}: {self.detail}{self.field and ' -> '}{self.field}"

class Variant1RedditAPIError(RedditAPIError):
	"""An error class denoting an error that was indicated in the
	response body of an API request, occurring when the remote API
	wishes to inform the client that a service request was carried
	out unsuccessfully.
	"""

	# {'json': {'errors': [['NO_TEXT', 'we need something here', 'title']]}}

	@property
	def codename(self):
		return self.errors[0].codename

	@property
	def detail(self):
		return self.errors[0].detail

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
		err_names = [err.codename for err in self.errors]
		return f'<{self.__class__.__name__} ({self.response}) {err_names}>'

	def __str__(self):
		err_count = len(self.errors)
		if err_count > 1:
			return f"multiple ({err_count}) errors encountered:\n" \
					+ '\n'.join(
						f"  {err.codename}: {err.detail}{err.field and ' -> '}{err.field}"
						for err in self.errors)

		return super().__str__()

class ContentCreationCooldown(Variant1RedditAPIError):
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
	codename: str
	detail: str
	field: str

def try_parse_reddit_error_items(data):
	errors = data.get('json', {}).get('errors')
	if errors:
		l = []
		for e in errors:
			name, message, field = e
			l.append(RedditErrorItem(name, message, field or ''))
		return l
	return None

def get_variant1_reddit_api_error(response, error_list):
	cls = Variant1RedditAPIError
	if (len(error_list) == 1) and (error_list[0].name == 'RATELIMIT'):
		cls = ContentCreationCooldown
	return cls(response, error_list)

def raise_for_variant1_reddit_api_error(resp, data):
	error_list = try_parse_reddit_error_items(data)
	if error_list is not None:
		raise get_variant1_reddit_api_error(resp, error_list)


class Variant2RedditAPIError(RedditAPIError):
	# {"fields": ["title"], "explanation": "this is too long (max: 50)", "message": "Bad Request", "reason": "TOO_LONG"}

	@property
	def codename(self):
		return self._codename

	@property
	def detail(self):
		return self._detail

	@property
	def field(self):
		return self._field

	def __init__(self, response, codename, detail, fields):
		super().__init__(response)
		self._codename = codename
		self._detail = detail
		self._field = fields[0] if fields else ''
		self.fields = fields

def raise_for_variant2_reddit_api_error(resp, data):
	if {'fields', 'explanation', 'message', 'reason'} == data.keys():
		codename = data['reason']
		detail = data['explanation']
		fields = data['fields']
		raise Variant2RedditAPIError(resp, codename, detail, fields)
