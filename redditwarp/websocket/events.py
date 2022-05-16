
from typing import Type, TypeVar
from dataclasses import dataclass

@dataclass
class Frame:
    opcode: int
    fin: bool
    data: bytes

    T = TypeVar('T', bound='Frame')

    @classmethod
    def make(cls: Type[T], opcode: int, data: bytes, fin: bool = True) -> T:
        return cls(opcode=opcode, data=data, fin=fin)


@dataclass
class Message:
    pass

@dataclass
class TextMessage(Message):
    data: str

@dataclass
class BytesMessage(Message):
    data: bytes


@dataclass
class Signal:
    pass

@dataclass
class ConnectionClosed(Signal):
    pass
