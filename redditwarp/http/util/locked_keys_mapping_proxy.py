
from __future__ import annotations
from typing import TypeVar, MutableMapping, Mapping, MutableSet, Optional, Iterator, IO, Any

from pprint import PrettyPrinter

K = TypeVar('K')
V = TypeVar('V')

class LockedKeysMappingProxy(MutableMapping[K, V]):
    def __init__(self,
        mapping: MutableMapping[K, V],
        locked_keys: Optional[MutableSet[K]] = None,
    ) -> None:
        self._store = mapping
        if locked_keys is None:
            locked_keys = set()
        self.locked_keys: MutableSet[K] = locked_keys

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._store})'

    def __contains__(self, item: object) -> bool:
        return item in self._store

    def __iter__(self) -> Iterator[K]:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def __getitem__(self, key: K) -> V:
        return self._store[key]

    def __setitem__(self, key: K, value: V) -> None:
        if key in self.locked_keys:
            return
        self._store[key] = value

    def __delitem__(self, key: K) -> None:
        if key in self.locked_keys:
            return
        del self._store[key]

    @staticmethod
    def _pprint(
        printer: PrettyPrinter,
        obj: Mapping[K, V],
        stream: IO[str],
        indent: int,
        allowance: int,
        context: Mapping[int, Any],
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
