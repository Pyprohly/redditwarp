
from __future__ import annotations
from typing import Any, Type, TypeVar, Mapping, MutableMapping, Iterable, Iterator, IO

from collections.abc import MutableMapping as MutableMapping_
from pprint import PrettyPrinter

V = TypeVar('V')

class AttributeDict(MutableMapping[str, V]):
	"""Wrap a mapping to expose its keys though attributes.

	MutableMapping methods (`.update()`, `.clear()`, etc.) take
	precedence over arbitrary attribute access. Indexing should instead
	be used to access the values of those names to avoid the collision.

	There are no restrictions on the key name. If a key can't be get/set
	as an attribute then indexing should be used.

	The underlying mapping object can be retrieved with `abs(self)`.
	"""

	__slots__ = ('_store',)

	def __init__(self, data: MutableMapping[str, V]):
		object.__setattr__(self, '_store', data)

	def __repr__(self) -> str:
		return f'{self.__class__.__name__}({self._store})'

	def __contains__(self, item: object) -> bool:
		return item in self._store

	def __len__(self) -> int:
		return len(self._store)

	def __iter__(self) -> Iterator[str]:
		return iter(self._store)

	def __abs__(self) -> MutableMapping[str, V]:
		return self._store

	def __dir__(self) -> Iterable[str]:
		return self.keys()

	def __getitem__(self, key: str) -> V:
		return self._store[key]

	def __setitem__(self, key: str, value: V) -> None:
		self._store[key] = value

	def __delitem__(self, key: str) -> None:
		del self._store[key]

	def __getattr__(self,
		name: str,
		mapping_type: Type[MutableMapping[str, V]] = MutableMapping_,
	) -> Any:
		"""Mapping-like objects are wrapped in an AttributeDict before being
		returned. This lets you dot chain into nested mappings.
		"""
		try:
			attr = self[name]
		except KeyError:
			raise AttributeError(repr(name)) from None

		if isinstance(attr, mapping_type):
			return type(self)(attr)
		return attr

	__setattr__ = __setitem__

	__delattr__ = __delitem__

	def __getstate__(self) -> MutableMapping[str, V]:
		return self._store

	def __setstate__(self, state: MutableMapping[str, V]) -> None:
		object.__setattr__(self, '_store', state)

	@staticmethod
	def _pprint(
		printer: PrettyPrinter,
		obj: AttributeDict,
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
		PrettyPrinter._dispatch[__repr__] = _pprint  # type: ignore[attr-defined] # noqa
