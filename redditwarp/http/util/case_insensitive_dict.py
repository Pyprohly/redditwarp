
from __future__ import annotations
from typing import TypeVar, Mapping, MutableMapping, Iterator, IO, cast, Tuple, Optional

from pprint import PrettyPrinter

V = TypeVar('V')

class CaseInsensitiveDict(MutableMapping[str, V]):
    __slots__ = ('_store',)
    _store: MutableMapping[str, Tuple[str, V]]

    def __init__(self, data: Optional[Mapping[str, V]] = None, **kwargs: V) -> None:
        self._store = {}
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __repr__(self) -> str:
        if self._store:
            return '%s(%r)' % (type(self).__name__, dict(self))
        return type(self).__name__ + '()'

    def __iter__(self) -> Iterator[str]:
        return (k for k, _ in self._store.values())

    def __len__(self) -> int:
        return len(self._store)

    def __setitem__(self, key: str, value: V) -> None:
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key: str) -> V:
        return self._store[key.lower()][1]

    def __delitem__(self, key: str) -> None:
        del self._store[key.lower()]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            if not isinstance(other, self.__class__):
                other = cast(Mapping, CaseInsensitiveDict(other))
            return other.items() == self.items()
        return NotImplemented

    def __getstate__(self) -> Mapping[str, Tuple[str, V]]:
        return self._store

    def __setstate__(self, state: Mapping[str, Tuple[str, V]]) -> None:
        object.__setattr__(self, '_store', state)

    @staticmethod
    def _pprint(
        printer: PrettyPrinter,
        obj: Mapping,
        stream: IO[str],
        indent: int,
        allowance: int,
        context: Mapping,
        level: int,
    ) -> None:
        cls_name = obj.__class__.__name__
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
