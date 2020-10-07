
from __future__ import annotations
from typing import Any, TypeVar, Mapping, MutableMapping, Iterable, Iterator, IO, Optional, Generic

from pprint import PrettyPrinter, pformat

V = TypeVar('V')

class AttributeMappingWrapper(Mapping[str, V]):
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

class MutableAttributeMappingWrapper(AttributeMappingWrapper[V], MutableMapping[str, V]):
    """Wrap a mapping to expose its keys though attributes.

    MutableMapping methods (`.update()`, `.clear()`, etc.) take
    precedence over arbitrary attribute access. Indexing should instead
    be used to access the values of those names to avoid the collision.

    There are no restrictions on the key name. If a key can't be get/set
    as an attribute then indexing should be used.

    The underlying mapping object can be retrieved with `abs(self)`.
    """
    _mutable_store: MutableMapping[str, V]

    def __init__(self, data: MutableMapping[str, V]) -> None:
        super().__init__(data)
        object.__setattr__(self, '_mutable_store', data)

    def __abs__(self) -> MutableMapping[str, V]:
        return self._mutable_store

    def __setitem__(self, key: str, value: V) -> None:
        self._mutable_store[key] = value

    def __delitem__(self, key: str) -> None:
        del self._mutable_store[key]

    # Have to write it the long way to make mypy notice this method.
    #__setattr__ = __setitem__
    def __setattr__(self, name: str, value: V) -> None:
        return self.__setitem__(name, value)

    __delattr__ = __delitem__


class _PrettyPrintingMixin(Generic[V]):
    _store: Mapping[str, V]

    def __repr__(self) -> str:
        return f'AttributeMappingWrapper({self._store})'

    def __str__(self) -> str:
        return pformat(self)

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
        AttributeMappingWrapper._pprint(
            printer,
            obj,
            stream,
            indent,
            allowance,
            context,
            level,
            cls_name='AttributeMappingWrapper',
        )

    if isinstance(getattr(PrettyPrinter, '_dispatch', None), dict):
        PrettyPrinter._dispatch[__repr__] = _pprint.__func__  # type: ignore[attr-defined]

class PrettyPrintingAttributeMappingWrapper(_PrettyPrintingMixin[V], AttributeMappingWrapper[V]): pass
class PrettyPrintingMutableAttributeMappingWrapper(_PrettyPrintingMixin[V], MutableAttributeMappingWrapper[V]): pass
