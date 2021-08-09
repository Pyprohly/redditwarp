
from __future__ import annotations

from ..exceptions import ArgInfoExceptionMixin

class RootException(Exception):
    pass

class ArgInfoException(ArgInfoExceptionMixin, RootException):
    pass


class TransportError(ArgInfoException):
    pass

class TimeoutException(ArgInfoException):
    pass


class MessageTypeMismatchException(RootException):
    pass

class ProtocolViolationException(RootException):
    pass

class InvalidStateException(RootException):
    pass

class ConnectionClosedException(RootException):
    pass
