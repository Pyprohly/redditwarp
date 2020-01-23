
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

class OAuth2ErrorResponse(AuthResponseError):
	"""
	As detailed in the OAuth2 spec. For more information see
	https://tools.ietf.org/html/rfc6749#section-5.2
	"""
	error_name: ClassVar[str] = ''

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

class InvalidRequest(OAuth2ErrorResponse):
	error_name = 'invalid_request'

class InvalidClient(OAuth2ErrorResponse):
	error_name = 'invalid_client'

class InvalidGrant(OAuth2ErrorResponse):
	error_name = 'invalid_grant'

class UnauthorizedClient(OAuth2ErrorResponse):
	error_name = 'unauthorized_client'

class UnsupportedGrantType(OAuth2ErrorResponse):
	error_name = 'unsupported_grant_type'

class InvalidScope(OAuth2ErrorResponse):
	error_name = 'invalid_scope'

oauth_error_response_classes = {
	cls.error_name: cls
	for cls in [
		OAuth2ErrorResponse,
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
