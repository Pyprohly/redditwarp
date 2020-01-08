
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .http import Response


class TransportError(Exception):
	pass


class HTTPError(Exception):
	pass

class HTTPResponseError(HTTPError):
	"""The request completed but the response indicated an error."""
	STATUS_CODE = -1

	def __init__(self, response: Response):
		self.response = response

class ClientError(HTTPResponseError):
	"""HTTP 4XX."""
class ServerError(HTTPResponseError):
	"""HTTP 5XX."""

class BadRequest(ClientError):
	STATUS_CODE = 400
class Unauthorized(ClientError):
	STATUS_CODE = 401

class InternalServerError(ServerError):
	STATUS_CODE = 500
class BadGateway(ServerError):
	STATUS_CODE = 502
class ServiceUnavailable(ServerError):
	STATUS_CODE = 503
class GatewayTimeout(ServerError):
	STATUS_CODE = 504

http_error_response_classes = {
	cls.STATUS_CODE: cls
	for cls in [
		HTTPResponseError,
		BadRequest,
		Unauthorized,
		InternalServerError,
		BadGateway,
		ServiceUnavailable,
		GatewayTimeout,
	]
}
