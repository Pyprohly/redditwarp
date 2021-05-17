
import struct

from . import const
from . import exceptions

def parse_close(data: bytes) -> tuple[int, str]:
    length = len(data)
    if length > 1:
        code, = struct.unpack("!H", data[:2])
        reason = data[2:].decode()
        return (code, reason)
    elif length == 0:
        return (1005, '')
    raise ValueError('close frame payload is too short')

def serialize_close(code: int, reason: str) -> bytes:
    return struct.pack("!H", code) + reason.encode()

def check_close_frame_close_code(code: int) -> None:
    if not (code in EXTERNAL_CLOSE_CODES or 3000 <= code < 5000):
        raise exceptions.ProtocolViolationError('invalid close frame close code')
