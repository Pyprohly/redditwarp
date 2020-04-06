
from __future__ import annotations
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
	from .response import Response

class TransportError(Exception):
	pass

class NetworkError(TransportError):
	pass

class TimeoutError(NetworkError):
	pass


class HTTPException(Exception):
	pass

class ResponseException(HTTPException):
	"""The request completed successfully but there was an issue with the response."""

	def __init__(self, response: Response):
		super().__init__(response)
		self.response = response

class StatusCodeException(ResponseException):
	STATUS_CODE = 0

class InformationalResponse(StatusCodeException):
	STATUS_CODE = -100
class SuccessfulResponse(StatusCodeException):
	STATUS_CODE = -200
class RedirectionResponse(StatusCodeException):
	STATUS_CODE = -300
class ClientError(StatusCodeException):
	STATUS_CODE = -400
class ServerError(StatusCodeException):
	STATUS_CODE = -500

class BadRequest(ClientError):
	STATUS_CODE = 400
class Unauthorized(ClientError):
	STATUS_CODE = 401
class Forbidden(ClientError):
	STATUS_CODE = 403
class NotFound(ClientError):
	STATUS_CODE = 404
class Conflict(ClientError):
	STATUS_CODE = 409
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

status_code_exception_class_by_status_code = {
	cls.STATUS_CODE: cls
	for cls in [
		# Client errors
		BadRequest,
		Unauthorized,
		Forbidden,
		NotFound,
		Conflict,
		PayloadTooLarge,
		TooManyRequests,

		# Server errors
		InternalServerError,
		BadGateway,
		ServiceUnavailable,
		GatewayTimeout,
	]
}

def get_status_code_exception_class_by_status_code(n: int) -> Type[StatusCodeException]:
	klass = status_code_exception_class_by_status_code.get(n)
	if klass is None:
		klass = StatusCodeException
		if 100 <= n < 200:
			klass = InformationalResponse
		elif 200 <= n < 300:
			klass = SuccessfulResponse
		elif 300 <= n < 400:
			klass = RedirectionResponse
		elif 400 <= n < 500:
			klass = ClientError
		elif 500 <= n < 600:
			klass = ServerError
	return klass

def raise_now(resp: Response) -> None:
	raise get_status_code_exception_class_by_status_code(resp.status)(resp)

def raise_for_status(resp: Response) -> None:
	if resp.status >= 400:
		raise_now(resp)
