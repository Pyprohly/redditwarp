
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Any, Dict
	from ..http.response import Response

from typing import ClassVar

from ..http.util import response_json


class AuthError(Exception):
	"""The root class for all OAuth authorization-related errors."""

class AuthResponseError(AuthError):
	def __init__(self, response: Response):
		super().__init__()
		self.response = response

class OAuth2ResponseError(AuthResponseError):
	"""
	As detailed in the OAuth2 spec. For more information see
	https://tools.ietf.org/html/rfc6749#section-5.2
	"""
	ERROR_NAME: ClassVar[str] = ''

	@classmethod
	def from_response(cls, response: Response):
		json_dict = response_json(response)
		return cls.from_response_and_json(response, json_dict)

	@classmethod
	def from_response_and_json(cls, response: Response, json: Dict[str, Any]):
		return cls(
			response,
			json.get('error_description', ''),
			json.get('error_uri', ''),
		)

	def __init__(self, response: Response,
			description: str = '', help_uri: str = ''):
		super().__init__(response)
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


class Unauthorized(AuthResponseError):
	pass
