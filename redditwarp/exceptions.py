
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, List, Mapping, MutableMapping
if TYPE_CHECKING:
	from .http.response import Response

from dataclasses import dataclass
from pprint import pformat

class RootException(Exception):
	pass

class BasicException(RootException):
	def __init__(self, exc_msg: object = None) -> None:
		super().__init__()
		self.exc_msg = exc_msg

	def __str__(self) -> str:
		if self.exc_msg is None:
			return self.exc_str()
		return str(self.exc_msg)

	def exc_str(self) -> str:
		return ''


class ClientError(BasicException):
	pass


class ResponseException(BasicException):
	def __init__(self, exc_msg: object = None, *, response: Response):
		super().__init__(exc_msg)
		self.response = response

class ServiceRequestError(ResponseException):
	pass

class AuthError(ServiceRequestError):
	pass

class APIError(ServiceRequestError):
	"""A base exception class denoting that something in the response body
	from an API request is amiss. Either an error was indicated by the API
	or the structure is of something the client isn't prepared to handle.
	"""

class HTTPStatusError(APIError):
	"""There was nothing useful to process in the response body and the
	response had a bad status code.
	"""



class ResponseContentError(APIError):
	pass

class UnidentifiedResponseContentError(ResponseContentError):
	"""The response body contains data that the client isn't prepared to handle."""

	def exc_str(self) -> str:
		return '\\\n\n** Please file a bug report with RedditWrap! **'

class UnidentifiedJSONLayoutResponseContentError(UnidentifiedResponseContentError):
	# Unused. This will never be raised.
	"""The response body contains JSON data that the client isn't prepared to handle."""

	def __init__(self, exc_msg: object = None, *, response: Response, json: MutableMapping[str, Any]):
		super().__init__(exc_msg=exc_msg, response=response)
		self.json = json

	def exc_str(self) -> str:
		return f'\\\n{pformat(self.json)}\n\n' \
				'** Please file a bug report with RedditWrap! **'


class UnacceptableResponseContentError(ResponseContentError):
	"""The response body contains data in a format that the client doesn’t want
	to or can't handle.
	"""

	def exc_str(self) -> str:
		return f'\\\n{self.response.data!r}\n\n' \
				'** Please file a bug report with RedditWrap! **'

class UnacceptableJSONLayoutResponseContentError(UnacceptableResponseContentError):
	"""The response body contains JSON data that the client isn't prepared to handle."""

	def __init__(self, exc_msg: object = None, *, response: Response, json: MutableMapping[str, Any]):
		super().__init__(exc_msg=exc_msg, response=response)
		self.json = json

	def exc_str(self) -> str:
		return f'\\\n{pformat(self.json)}\n\n' \
				'** Please file a bug report with RedditWrap! **'


class HTMLDocumentResponseContentError(ResponseContentError):
	pass

class UserAgentRequired(ResponseException):
	pass


def get_response_content_error(resp: Response) -> Exception:
	if resp.data.lower().startswith(b'<!doctype html>'):
		if b'>user agent required</' in resp.data:
			return UserAgentRequired(
					'the Reddit API wants you to set a user-agent',
					response=resp)
		return HTMLDocumentResponseContentError(response=resp)
	return UnidentifiedResponseContentError(response=resp)

def raise_for_json_layout_content_error(resp: Response, json_data: MutableMapping[str, Any]) -> None:
	if {'jquery', 'success'} <= json_data.keys():
		raise UnacceptableJSONLayoutResponseContentError(response=resp, json=json_data)



class RedditAPIError(APIError):
	"""An error class denoting an error that was indicated in the
	response body of an API request, occurring when the remote API
	wishes to inform the client that a service request was carried
	out unsuccessfully.
	"""

	@property
	def codename(self) -> str:
		return ''

	@property
	def detail(self) -> str:
		return ''

	@property
	def field(self) -> str:
		return ''

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__} ({self.response})>'

	def __str__(self) -> str:
		cn = self.codename
		de = self.detail
		fd = self.field
		return f"{cn}: {de}{fd and f' -> {fd}'}"

class Variant1RedditAPIError(RedditAPIError):
	"""An error class denoting an error that was indicated in the
	response body of an API request, occurring when the remote API
	wishes to inform the client that a service request was carried
	out unsuccessfully.
	"""

	# {'json': {'errors': [['NO_TEXT', 'we need something here', 'title']]}}

	@property
	def codename(self) -> str:
		return self.errors[0].codename

	@property
	def detail(self) -> str:
		return self.errors[0].detail

	@property
	def field(self) -> str:
		return self.errors[0].field

	def __init__(self, exc_msg: object = None, *, response: Response, errors: List[RedditErrorItem]):
		"""
		Parameters
		----------
		response: :class:`.http.Response`
		errors: List[:class:`.RedditErrorItem`]
		"""
		super().__init__(exc_msg=exc_msg, response=response)
		errors[0]
		self.errors = errors

	def __repr__(self) -> str:
		err_names = [err.codename for err in self.errors]
		return f'<{self.__class__.__name__} ({self.response}) {err_names}>'

	def __str__(self) -> str:
		err_count = len(self.errors)
		if err_count > 1:
			return f"multiple ({err_count}) errors encountered:\n" \
					+ '\n'.join(
						f"  {err.codename}: {err.detail}{err.field and f' -> {err.field}'}"
						for err in self.errors)

		return super().__str__()

class ContentCreationCooldown(Variant1RedditAPIError):
	"""Used over RedditAPIError when the error items list contains
	a RATELIMIT error, and it is the only error in the list.
	"""

	def __str__(self) -> str:
		return super().__str__() + '''

Looks like you hit a content creation ratelimit. This can happen when
your account has low karma or no verified email.
'''

@dataclass
class RedditErrorItem:
	codename: str
	detail: str
	field: str

def try_parse_reddit_error_items(data: Mapping[str, Any]) -> Optional[List[RedditErrorItem]]:
	errors = data.get('json', {}).get('errors')
	if errors:
		l = []
		for e in errors:
			name, message, field = e
			l.append(RedditErrorItem(name, message, field or ''))
		return l
	return None

def get_variant1_reddit_api_error(response: Response, error_list: List[RedditErrorItem]) -> Variant1RedditAPIError:
	cls = Variant1RedditAPIError
	if (len(error_list) == 1) and (error_list[0].codename == 'RATELIMIT'):
		cls = ContentCreationCooldown
	return cls(response=response, errors=error_list)

def raise_for_variant1_reddit_api_error(resp: Response, data: Mapping[str, Any]) -> None:
	error_list = try_parse_reddit_error_items(data)
	if error_list is not None:
		raise get_variant1_reddit_api_error(resp, error_list)


class Variant2RedditAPIError(RedditAPIError):
	# {"fields": ["title"], "explanation": "this is too long (max: 50)", "message": "Bad Request", "reason": "TOO_LONG"}

	@property
	def codename(self) -> str:
		return self._codename

	@property
	def detail(self) -> str:
		return self._detail

	@property
	def field(self) -> str:
		return self._field

	def __init__(self, exc_msg: object = None, *, response: Response, codename: str, detail: str, fields: str):
		super().__init__(exc_msg=exc_msg, response=response)
		self._codename = codename
		self._detail = detail
		self._field = fields[0] if fields else ''
		self.fields = fields

def raise_for_variant2_reddit_api_error(resp: Response, data: Mapping[str, Any]) -> None:
	if data.keys() == {'fields', 'explanation', 'message', 'reason'}:
		codename = data['reason']
		detail = data['explanation']
		fields = data['fields']
		raise Variant2RedditAPIError(
			response=resp,
			codename=codename,
			detail=detail,
			fields=fields,
		)
