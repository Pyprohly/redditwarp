
from __future__ import annotations
from typing import Any, TypeVar, Mapping, MutableMapping, Iterable, Iterator, IO, Generic, cast

from pprint import PrettyPrinter

V = TypeVar('V')

class AttributeMappingWrapper(Generic[V], MutableMapping[str, V]):
    """Wrap a mapping to expose its keys though attributes.

    MutableMapping methods (`.update()`, `.clear()`, etc.) take
    precedence over arbitrary attribute access. Indexing should instead
    be used to access the values of those names to avoid the collision.

    There are no restrictions on the key name. If a key can't be get/set
    as an attribute then indexing should be used.

    The underlying mapping object can be retrieved with `abs(self)`.
    """
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

    def __abs__(self) -> Mapping[str, V]:
        return self._store

    def __dir__(self) -> Iterable[str]:
        return self.keys()

    def __getitem__(self, key: str) -> V:
        return self._store[key]

    def __setitem__(self, key: str, value: V) -> None:
        cast(MutableMapping[str, V], self._store)[key] = value

    def __delitem__(self, key: str) -> None:
        del cast(MutableMapping[str, V], self._store)[key]

    def __getattr__(self,
        name: str,
    ) -> Any:
        """Mapping-like objects are wrapped in an AttributeMappingWrapper before being
        returned. This lets you dot chain into nested mappings.
        """
        try:
            attr = self[name]
        except KeyError:
            raise AttributeError(repr(name)) from None

        if isinstance(attr, Mapping):
            return type(self)(attr)
        return attr

    #__setattr__ = __setitem__
    # Do it the long way. Make mypy happy.
    def __setattr__(self, name: str, value: V) -> None:
        return self.__setitem__(name, value)

    __delattr__ = __delitem__

    def __getstate__(self) -> Mapping[str, V]:
        return self._store

    def __setstate__(self, state: Mapping[str, V]) -> None:
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
        PrettyPrinter._dispatch[__repr__] = _pprint.__func__  # type: ignore[attr-defined] # noqa
