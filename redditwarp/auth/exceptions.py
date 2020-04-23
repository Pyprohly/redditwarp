
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Any, Dict
	from ..http.response import Response

from typing import Type, TypeVar, ClassVar

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


class ResponseException(BasicException):
	def __init__(self, exc_msg: object = None, *, response: Response) -> None:
		super().__init__(exc_msg)
		self.response = response

	def exc_str(self) -> str:
		return str(self.response)

class HTTPStatusError(ResponseException):
	pass



class ResponseContentError(ResponseException):
	pass

class UnidentifiedResponseContentError(ResponseContentError):
	pass

class HTMLDocumentResponseContentError(ResponseContentError):
	pass

class PossiblyBlacklistedUserAgent(HTMLDocumentResponseContentError):
	pass


def get_response_content_error(resp):
	if resp.data.lower().startswith(b'<!doctype html>'):
		if (b'<p>you are not allowed to do that</p>\n\n &mdash; access was denied to this resource.</div>'
				in resp.data):
			return PossiblyBlacklistedUserAgent(resp)
		return HTMLDocumentResponseContentError(resp)
	return UnidentifiedResponseContentError(resp)



T = TypeVar('T', bound='OAuth2ResponseError')

class OAuth2ResponseError(ResponseException):
	"""
	As detailed in the OAuth2 spec. For more information see
	https://tools.ietf.org/html/rfc6749#section-5.2
	"""
	ERROR_NAME: ClassVar[str] = ''

	@classmethod
	def from_response_and_json(cls: Type[T], response: Response, json: Dict[str, Any]) -> T:
		return cls(
			response=response,
			error_name=json.get('error', ''),
			description=json.get('error_description', ''),
			help_uri=json.get('error_uri', ''),
		)

	def __init__(self, exc_msg: object = None, *, response: Response, error_name: str = '',
			description: str = '', help_uri: str = '') -> None:
		super().__init__(exc_msg=exc_msg, response=response)
		self.error_name = error_name
		self.description = description
		self.help_uri = help_uri

class InvalidRequest(OAuth2ResponseError):
	ERROR_NAME = 'invalid_request'

class InvalidClient(OAuth2ResponseError):
	ERROR_NAME = 'invalid_client'

class InvalidGrant(OAuth2ResponseError):
	ERROR_NAME = 'invalid_grant'

class UnauthorizedClient(OAuth2ResponseError):
	ERROR_NAME = 'unauthorized_client'

class UnsupportedGrantType(OAuth2ResponseError):
	ERROR_NAME = 'unsupported_grant_type'

class InvalidScope(OAuth2ResponseError):
	ERROR_NAME = 'invalid_scope'

oauth2_response_error_class_by_error_name = {
	cls.ERROR_NAME: cls
	for cls in [
		OAuth2ResponseError,
		InvalidRequest,
		InvalidClient,
		InvalidGrant,
		UnauthorizedClient,
		UnsupportedGrantType,
		InvalidScope,
	]
}
