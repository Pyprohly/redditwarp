
from __future__ import annotations
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from .response import Response

class RootException(Exception):
    pass

class InfoException(RootException):
    def __init__(self, arg: object = None) -> None:
        super().__init__()
        self.arg = arg

    def __str__(self) -> str:
        if self.arg is None:
            return self.get_default_message()
        return str(self.arg)

    def get_default_message(self) -> str:
        return ''


class TransportError(InfoException):
    pass

class NetworkError(TransportError):
    pass

class TimeoutError(NetworkError):
    pass


class HTTPException(InfoException):
    pass

class ResponseException(HTTPException):
    """The request completed successfully but there was an issue with the response."""

    def __init__(self, arg: object = None, *, response: Response) -> None:
        super().__init__(arg)
        self.response = response

    def __str__(self) -> str:
        return str(self.response)

class StatusCodeException(ResponseException):
    STATUS_CODE = 0

class InformationalResponse(StatusCodeException):
    STATUS_CODE = -100
class SuccessfulResponse(StatusCodeException):
    STATUS_CODE = -200
class RedirectionResponse(StatusCodeException):
    STATUS_CODE = -300
class ClientErrorResponse(StatusCodeException):
    STATUS_CODE = -400
class ServerErrorResponse(StatusCodeException):
    STATUS_CODE = -500

class BadRequest(ClientErrorResponse):
    STATUS_CODE = 400
class Unauthorized(ClientErrorResponse):
    STATUS_CODE = 401
class Forbidden(ClientErrorResponse):
    STATUS_CODE = 403
class NotFound(ClientErrorResponse):
    STATUS_CODE = 404
class Conflict(ClientErrorResponse):
    STATUS_CODE = 409
class PayloadTooLarge(ClientErrorResponse):
    STATUS_CODE = 413
class URITooLong(ClientErrorResponse):
    STATUS_CODE = 414
class TooManyRequests(ClientErrorResponse):
    STATUS_CODE = 429

class InternalServerError(ServerErrorResponse):
    STATUS_CODE = 500
class BadGateway(ServerErrorResponse):
    STATUS_CODE = 502
class ServiceUnavailable(ServerErrorResponse):
    STATUS_CODE = 503
class GatewayTimeout(ServerErrorResponse):
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
        URITooLong,
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
            klass = ClientErrorResponse
        elif 500 <= n < 600:
            klass = ServerErrorResponse
    return klass

def raise_now(resp: Response) -> None:
    raise get_status_code_exception_class_by_status_code(resp.status)(response=resp)

def raise_for_status(resp: Response) -> None:
    if resp.status >= 400:
        raise_now(resp)
