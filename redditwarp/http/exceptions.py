
from __future__ import annotations
from typing import Mapping

from http import HTTPStatus

from ..exceptions import ArgExcMixin

class ArgExc(ArgExcMixin):
    pass


class TransportError(ArgExc):
    pass

class TimeoutException(ArgExc):
    pass

class StatusCodeException(ArgExc):
    STATUS_CODE = 0

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
            klass = StatusCodeExceptionTypes.InformationalResponseException
        elif 200 <= n <= 299:
            klass = StatusCodeExceptionTypes.SuccessfulResponseException
        elif 300 <= n <= 399:
            klass = StatusCodeExceptionTypes.RedirectionResponseException
        elif 400 <= n <= 499:
            klass = StatusCodeExceptionTypes.ClientErrorResponseException
        elif 500 <= n <= 599:
            klass = StatusCodeExceptionTypes.ServerErrorResponseException
    return klass

def status_successful(n: int) -> bool:
    return 200 <= n <= 299

def raise_now(n: int) -> None:
    raise get_status_code_exception_class_by_status_code(n)(status_code=n)

def raise_for_status(n: int) -> None:
    if not status_successful(n):
        raise_now(n)
