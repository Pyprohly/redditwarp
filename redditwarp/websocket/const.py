
from enum import IntEnum

class Side(IntEnum):
    NONE = 0
    CLIENT = 1
    SERVER = 2

class ConnectionState(IntEnum):
    NONE = 0
    CONNECTING = 1
    OPEN = 2
    CLOSE_SENT = 3
    CLOSE_RECEIVED = 4
    CLOSED = 5

class Opcode(IntEnum):
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA

    @staticmethod
    def is_data_frame_opcode(v: int) -> bool:
        return (v & 0x8) == 0

    @staticmethod
    def is_control_frame_opcode(v: int) -> bool:
        return (v & 0x8) != 0

AUTHORITATIVE_CLOSE_FRAME_CLOSE_CODES = {
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

FORBIDDEN_CLOSE_FRAME_CLOSE_CODES = {
    1005,
    1006,
    1015,
}
