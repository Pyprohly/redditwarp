
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .response import Response

class TransportError(Exception):
	pass

class TimeoutError(TransportError):
	pass


class HTTPResponseError(Exception):
	"""The request completed but the response indicated an error."""
	STATUS_CODE = 0

	def __init__(self, response: Response):
		super().__init__()
		self.response = response

class ClientError(HTTPResponseError):
	STATUS_CODE = -400
class ServerError(HTTPResponseError):
	STATUS_CODE = -500

class BadRequest(ClientError):
	STATUS_CODE = 400
class Unauthorized(ClientError):
	STATUS_CODE = 401
class Forbidden(ClientError):
	STATUS_CODE = 403
class NotFound(ClientError):
	STATUS_CODE = 404
class PayloadTooLarge(ClientError):
	STATUS_CODE = 413
class TooManyRequests(ClientError):
	STATUS_CODE = 429

class InternalServerError(ServerError):
	STATUS_CODE = 500
class BadGateway(ServerError):
	STATUS_CODE = 502
class ServiceUnavailable(ServerError):
	STATUS_CODE = 503
class GatewayTimeout(ServerError):
	STATUS_CODE = 504

http_response_error_class_by_status_code = {
	cls.STATUS_CODE: cls
	for cls in [
		HTTPResponseError,
		BadRequest,
		Unauthorized,
		NotFound,
		PayloadTooLarge,
		TooManyRequests,

		InternalServerError,
		BadGateway,
		ServiceUnavailable,
		GatewayTimeout,
	]
}

def get_http_response_error_class_by_status_code(n):
	return http_response_error_class_by_status_code.get(n, HTTPResponseError)
