
from typing import Type, TypeVar
from dataclasses import dataclass

class Event:
    pass

@dataclass
class Frame(Event):
    opcode: int
    fin: bool
    data: bytes

    T = TypeVar('T', bound='Frame')

    @classmethod
    def make(cls: Type[T], opcode: int, data: bytes, fin: bool = True) -> T:
        return cls(opcode=opcode, data=data, fin=fin)


@dataclass
class Message(Event):
    pass

@dataclass
class TextMessage(Message):
    data: str

@dataclass
class BytesMessage(Message):
    data: bytes


@dataclass
class Signal(Event):
    pass

@dataclass
class ConnectionClosed(Event):
    pass
