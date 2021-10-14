
from __future__ import annotations

from ..exceptions import ArgExcMixin

class ArgExc(ArgExcMixin):
    pass


class TransportError(ArgExc):
    pass

class TimeoutException(ArgExc):
    pass


class MessageTypeMismatchException(ArgExc):
    pass

class ProtocolViolationException(ArgExc):
    pass

class InvalidStateException(ArgExc):
    pass

class ConnectionClosedException(ArgExc):
    pass
