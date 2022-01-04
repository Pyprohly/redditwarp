
from __future__ import annotations

from enum import IntEnum

class Side(IntEnum):
    NONE = 0
    CLIENT = 1
    SERVER = 2

class ConnectionState(IntEnum):
    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3

class Opcode(IntEnum):
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA

'''
def is_data_frame_opcode(v: int) -> bool:
    return (v & 0x8) == 0

def is_control_frame_opcode(v: int) -> bool:
    return (v & 0x8) != 0
'''

AUTHORITATIVE_CLOSE_FRAME_CLOSE_CODES: set[int] = {
    1000,
    1001,
    1002,
    1003,
    1007,
    1008,
    1009,
    1010,
    1011,
    1012,
    1013,
    1014,
}

FORBIDDEN_CLOSE_FRAME_CLOSE_CODES: set[int] = {
    1005,
    1006,
    1015,
}
