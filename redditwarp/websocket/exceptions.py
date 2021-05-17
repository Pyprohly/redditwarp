
from __future__ import annotations

from ..exceptions import ArgInfoExceptionMixin

class RootException(Exception):
    pass

class ArgInfoException(ArgInfoExceptionMixin, RootException):
    pass


class NetworkError(ArgInfoException):
    pass

class TransportError(NetworkError):
    pass

class TimeoutError(NetworkError):
    pass


class MessageTypeMismatchException(RootException):
    pass

class ProtocolViolationException(RootException):
    pass

class InvalidStateException(RootException):
    pass
