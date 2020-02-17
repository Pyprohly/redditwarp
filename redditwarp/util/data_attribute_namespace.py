
import collections.abc
from pprint import PrettyPrinter, pformat

class DataAttributeNamespace(collections.abc.Collection):
	def __init__(self, instance):
		self._instance = instance

	def __repr__(self):
		return f'{self.__class__.__name__} %r' % self._data_attribute_dict()

	def __iter__(self):
		return iter(self._data_attribute_iter())

	def __len__(self):
		return sum(1 for _ in self._data_attribute_iter())

	def __contains__(self, item):
		try:
			value = getattr(self._instance, item)
		except AttributeError:
			return False
		return not callable(value)

	def __getattr__(self, name):
		value = getattr(self._instance, name)
		if callable(value):
			raise AttributeError(f'{self._instance.__class__.__name__!r} has no data attribute {name!r}')
		return value

	def _data_attribute_iter(self):
		for name in dir(self._instance):
			if name.startswith('_'):
				continue
			value = getattr(self._instance, name)
			if value is self or callable(value):
				continue
			yield name

	def _data_attribute_dict(self):
		return {a: getattr(self._instance, a) for a in self._data_attribute_iter()}

	def _pprint(printer, obj, stream, indent, allowance, context, level):
		cls_name = obj.__class__.__name__
		stream.write(f'{cls_name} ')
		printer._format(
			obj._data_attribute_dict(),
			stream,
			indent + len(cls_name) + 1,
			allowance + 1,
			context,
			level,
		)

	if isinstance(getattr(PrettyPrinter, '_dispatch', None), dict):
		PrettyPrinter._dispatch[__repr__] = _pprint


class AttributeCollection(DataAttributeNamespace):
	def __str__(self):
		return pformat(self)

	def __getitem__(self, key):
		try:
			value = getattr(self._instance, key)
		except AttributeError:
			raise KeyError(key)
		if callable(value):
			raise KeyError(key)
		return value
