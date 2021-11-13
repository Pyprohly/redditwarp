
from __future__ import annotations
from typing import Any, TypeVar, Mapping, Iterable, Iterator, IO, Optional, Sequence, overload, Union

from pprint import PrettyPrinter

V = TypeVar('V')

class AttributeMappingProxy(Mapping[str, V]):
    __slots__ = ('_store',)
    _store: Mapping[str, V]

    def __init__(self, data: Mapping[str, V]) -> None:
        object.__setattr__(self, '_store', data)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._store})'

    def __contains__(self, item: object) -> bool:
        return item in self._store

    def __len__(self) -> int:
        return len(self._store)

    def __iter__(self) -> Iterator[str]:
        return iter(self._store)

    def __dir__(self) -> Iterable[str]:
        return self.keys()

    def __abs__(self) -> Mapping[str, V]:
        return self._store

    def __getitem__(self, key: str) -> V:
        return self._store[key]

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(repr(name)) from None

    def __getstate__(self) -> Mapping[str, V]:
        return self._store

    def __setstate__(self, state: Mapping[str, V]) -> None:
        object.__setattr__(self, '_store', state)

    @staticmethod
    def _pprint(
        printer: PrettyPrinter,
        obj: Mapping[str, V],
        stream: IO[str],
        indent: int,
        allowance: int,
        context: Mapping[int, Any],
        level: int,
        *,
        cls_name: Optional[str] = None,
    ) -> None:
        cls_name = obj.__class__.__name__ if cls_name is None else cls_name
        stream.write(cls_name + '(')
        printer._format(  # type: ignore[attr-defined]
            dict(obj),
            stream,
            indent + len(cls_name) + 1,
            allowance + 1,
            context,
            level,
        )
        stream.write(')')

    if isinstance(getattr(PrettyPrinter, '_dispatch', None), dict):
        PrettyPrinter._dispatch[__repr__] = _pprint.__func__  # type: ignore[attr-defined]


class MappingRecursiveAttributeMappingProxy(AttributeMappingProxy[V]):
    def __getattr__(self, name: str) -> Any:
        attr = super().__getattr__(name)
        if isinstance(attr, Mapping):
            return MappingRecursiveAttributeMappingProxy(attr)
        return attr


class AttributeMappingProxySequence(Sequence[Any]):
    def __init__(self, data: Sequence[Any]):
        self._elements: Sequence[Any] = data

    def __len__(self) -> int:
        return len(self._elements)

    def __contains__(self, item: object) -> bool:
        return item in self._elements

    def __iter__(self) -> Iterator[Any]:
        return iter(self._elements)

    @overload
    def __getitem__(self, index: int) -> Any: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[Any]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[Any, Sequence[Any]]:
        item = self._elements[index]
        if isinstance(item, Mapping):
            return MappingAndSequenceRecursiveAttributeMappingProxy(item)
        if isinstance(item, Sequence):
            return AttributeMappingProxySequence(item)
        return item

class MappingAndSequenceRecursiveAttributeMappingProxy(AttributeMappingProxy[V]):
    def __getattr__(self, name: str) -> Any:
        attr = super().__getattr__(name)
        if isinstance(attr, Mapping):
            return MappingAndSequenceRecursiveAttributeMappingProxy(attr)
        elif isinstance(attr, Sequence):
            return AttributeMappingProxySequence(attr)
        return attr
