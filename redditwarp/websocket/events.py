
from typing import Type, TypeVar
from dataclasses import dataclass

T = TypeVar('T')

class Event:
    pass

@dataclass
class Frame(Event):
    opcode: int
    fin: bool
    data: bytes

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
