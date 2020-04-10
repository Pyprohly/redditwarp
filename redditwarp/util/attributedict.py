
from collections.abc import Mapping, MutableMapping
from pprint import PrettyPrinter

class AttributeDict(MutableMapping):
	"""Wrap a mapping to expose its keys though attributes.

	MutableMapping methods (`.update()`, `.clear()`, etc.) take
	precedence over arbitrary attribute access. Indexing should instead
	be used to access the values of those names to avoid the collision.

	There are no restrictions on the key name. If a key can't be get/set
	as an attribute then indexing should be used.

	The underlying mapping object can be retrieved with `abs(self)`.
	"""

	__slots__ = ('_store',)

	def __init__(self, data: MutableMapping):
		object.__setattr__(self, '_store', data)

	def __repr__(self):
		return f'{self.__class__.__name__}({self._store})'

	def __contains__(self, item):
		return item in self._store

	def __len__(self):
		return len(self._store)

	def __iter__(self):
		return iter(self._store)

	def __abs__(self):
		return self._store

	def __dir__(self):
		return self.keys()

	def __getitem__(self, key):
		return self._store[key]

	def __setitem__(self, key, value):
		self._store[key] = value

	def __delitem__(self, key):
		del self._store[key]

	def __getattr__(self, name, mapping_type=Mapping):
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

	def __getstate__(self):
		return self._store

	def __setstate__(self, state):
		object.__setattr__(self, '_store', state)

	def _pprint(printer, obj, stream, indent, allowance, context, level):
		cls_name = obj.__class__.__name__
		stream.write(cls_name + '(')
		printer._format(
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
