
from __future__ import annotations
from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from .response import Response

from ..exceptions import ArgInfoExceptionMixin

class RootException(Exception):
    pass

class ArgInfoException(ArgInfoExceptionMixin, RootException):
    pass


class TransportError(ArgInfoException):
    pass

class NetworkError(TransportError):
    pass

class TimeoutError(NetworkError):
    pass


class HTTPException(ArgInfoException):
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

class InformationalResponseException(StatusCodeException):
    STATUS_CODE = -100
class SuccessfulResponseException(StatusCodeException):
    STATUS_CODE = -200
class RedirectionResponseException(StatusCodeException):
    STATUS_CODE = -300
class ClientErrorResponseException(StatusCodeException):
    STATUS_CODE = -400
class ServerErrorResponseException(StatusCodeException):
    STATUS_CODE = -500

class BadRequest(ClientErrorResponseException):
    STATUS_CODE = 400
class Unauthorized(ClientErrorResponseException):
    STATUS_CODE = 401
class Forbidden(ClientErrorResponseException):
    STATUS_CODE = 403
class NotFound(ClientErrorResponseException):
    STATUS_CODE = 404
class Conflict(ClientErrorResponseException):
    STATUS_CODE = 409
class PayloadTooLarge(ClientErrorResponseException):
    STATUS_CODE = 413
class URITooLong(ClientErrorResponseException):
    STATUS_CODE = 414
class TooManyRequests(ClientErrorResponseException):
    STATUS_CODE = 429

class InternalServerError(ServerErrorResponseException):
    STATUS_CODE = 500
class BadGateway(ServerErrorResponseException):
    STATUS_CODE = 502
class ServiceUnavailable(ServerErrorResponseException):
    STATUS_CODE = 503
class GatewayTimeout(ServerErrorResponseException):
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
            klass = InformationalResponseException
        elif 200 <= n < 300:
            klass = SuccessfulResponseException
        elif 300 <= n < 400:
            klass = RedirectionResponseException
        elif 400 <= n < 500:
            klass = ClientErrorResponseException
        elif 500 <= n < 600:
            klass = ServerErrorResponseException
    return klass

def raise_now(resp: Response) -> None:
    raise get_status_code_exception_class_by_status_code(resp.status)(response=resp)

def raise_for_status(resp: Response) -> None:
    if resp.status >= 400:
        raise_now(resp)
