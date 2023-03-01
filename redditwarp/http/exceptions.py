
from __future__ import annotations
from typing import Mapping, ClassVar

from http import HTTPStatus

from ..exceptions import ArgExcMixin

class ArgExc(ArgExcMixin):
    pass


class TransportError(ArgExc):
    """A catch-all exception for HTTP transport library errors."""

class TimeoutException(ArgExc):
    """A timeout exception class to wrap timeout errors from HTTP transport libraries."""

class StatusCodeException(ArgExc):
    """An exception class representing HTTP status codes as errors."""

    __match_args__ = ('status_code',)

    STATUS_CODE: ClassVar[int] = 0

    def __init__(self, arg: object = None, *, status_code: int) -> None:
        super().__init__(arg)
        self.status_code: int = status_code

    def get_default_message(self) -> str:
        sts = self.status_code
        try:
            return f"{sts} {HTTPStatus(sts).phrase}"
        except ValueError:
            return f"{sts}"

class StatusCodeExceptionTypes:
    class InformationalStatusCodeException(StatusCodeException):
        STATUS_CODE: ClassVar[int] = -100
    class SuccessfulStatusCodeException(StatusCodeException):
        STATUS_CODE: ClassVar[int] = -200
    class RedirectionStatusCodeException(StatusCodeException):
        STATUS_CODE: ClassVar[int] = -300
    class ClientErrorStatusCodeException(StatusCodeException):
        STATUS_CODE: ClassVar[int] = -400
    class ServerErrorStatusCodeException(StatusCodeException):
        STATUS_CODE: ClassVar[int] = -500

    class BadRequest(ClientErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 400
    class Unauthorized(ClientErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 401
    class Forbidden(ClientErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 403
    class NotFound(ClientErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 404
    class Conflict(ClientErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 409
    class PayloadTooLarge(ClientErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 413
    class URITooLong(ClientErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 414
    class TooManyRequests(ClientErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 429

    class InternalServerError(ServerErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 500
    class BadGateway(ServerErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 502
    class ServiceUnavailable(ServerErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 503
    class GatewayTimeout(ServerErrorStatusCodeException):
        STATUS_CODE: ClassVar[int] = 504

status_code_exception_class_by_status_code: Mapping[int, type[StatusCodeException]] = {
    cls.STATUS_CODE: cls
    for cls in [
        # Client errors
        StatusCodeExceptionTypes.BadRequest,
        StatusCodeExceptionTypes.Unauthorized,
        StatusCodeExceptionTypes.Forbidden,
        StatusCodeExceptionTypes.NotFound,
        StatusCodeExceptionTypes.Conflict,
        StatusCodeExceptionTypes.PayloadTooLarge,
        StatusCodeExceptionTypes.URITooLong,
        StatusCodeExceptionTypes.TooManyRequests,

        # Server errors
        StatusCodeExceptionTypes.InternalServerError,
        StatusCodeExceptionTypes.BadGateway,
        StatusCodeExceptionTypes.ServiceUnavailable,
        StatusCodeExceptionTypes.GatewayTimeout,
    ]
}

def get_status_code_exception_class_by_status_code(n: int) -> type[StatusCodeException]:
    klass = status_code_exception_class_by_status_code.get(n)
    if klass is None:
        klass = StatusCodeException
        if 100 <= n <= 199:
            klass = StatusCodeExceptionTypes.InformationalStatusCodeException
        elif 200 <= n <= 299:
            klass = StatusCodeExceptionTypes.SuccessfulStatusCodeException
        elif 300 <= n <= 399:
            klass = StatusCodeExceptionTypes.RedirectionStatusCodeException
        elif 400 <= n <= 499:
            klass = StatusCodeExceptionTypes.ClientErrorStatusCodeException
        elif 500 <= n <= 599:
            klass = StatusCodeExceptionTypes.ServerErrorStatusCodeException
    return klass


def is_successful_status(n: int) -> bool:
    """Return true if `200 <= n < 300`."""
    return 200 <= n <= 299

def raise_now(n: int) -> None:
    """Raises a :class:`.StatusCodeException` exception type based on the given HTTP status number."""
    raise get_status_code_exception_class_by_status_code(n)(status_code=n)

def ensure_successful_status(n: int) -> None:
    """Raises a :class:`.StatusCodeException` exception if `is_successful_status(n)` returns false."""
    if not is_successful_status(n):
        raise_now(n)
