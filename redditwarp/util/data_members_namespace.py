
from __future__ import annotations
from typing import Any, Dict, Collection, TypeVar, Iterator, Iterable, Tuple, Mapping, IO, cast

import inspect
from ast import literal_eval
import reprlib
from pprint import PrettyPrinter
from io import StringIO


rep = reprlib.Repr()
rep.maxlevel = 1
rep.maxstring = 250
rep.maxother = 250
reprepr = rep.repr

class StrReprStr(str):
	def __repr__(self) -> str:
		return str(self)

def neat_repr_dict(d: Dict) -> Dict:
	return {
		k: (literal_eval(reprepr(v)) if isinstance(v, str) else StrReprStr(reprepr(v)))
		for k, v in d.items()
	}


ppr = PrettyPrinter()
ppr_format = ppr._format  # type: ignore[attr-defined] # noqa

def pretty_format(obj: object) -> str:
	# This function ensures `obj`'s pretty-print-formatted string is
	# returned, since `pprint.pformat()` only invokes an object's
	# pretty printer if its __repr__ is long enough.
	sio = StringIO()
	ppr_format(obj, sio, 0, 999999, {}, 0)
	return sio.getvalue()


T = TypeVar('T')

class DataMembersNamespace(Collection[str]):
	def __init__(self, instance: T):
		self._instance = instance

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}({self._instance})>'

	def __str__(self) -> str:
		return pretty_format(self)

	def __iter__(self) -> Iterator[str]:
		return (k for k, v in self._data_members())

	def __len__(self) -> int:
		return sum(1 for _ in self._data_members())

	def __contains__(self, item: object) -> bool:
		try:
			value = getattr(self._instance, cast(str, item))
		except AttributeError:
			return False
		return not inspect.ismethod(value)

	def __getattr__(self, name: str) -> Any:
		value = getattr(self._instance, name)
		if inspect.ismethod(value):
			raise AttributeError(f'{self._instance.__class__.__name__!r} has no data attribute {name!r}')
		return value

	def __dir__(self) -> Iterable[str]:
		return list(self)

	def _data_members(self) -> Iterator[Tuple[str, Any]]:
		for name, value in inspect.getmembers(self._instance, (lambda x: not inspect.ismethod(x))):
			if value is self:
				continue
			if name.startswith('_'):
				continue
			yield name, value

	@staticmethod
	def _pprint(
		printer: PrettyPrinter,
		obj: DataMembersNamespace,
		stream: IO[str],
		indent: int,
		allowance: int,
		context: Mapping,
		level: int,
	) -> None:
		leader = 'data members: '
		stream.write(leader)
		printer._format(  # type: ignore[attr-defined]
			neat_repr_dict(dict(obj._data_members())),
			stream,
			indent + len(leader),
			allowance,
			context,
			level,
		)

	if isinstance(getattr(PrettyPrinter, '_dispatch', None), dict):
		PrettyPrinter._dispatch[__repr__] = _pprint  # type: ignore[attr-defined] # noqa


class AttributeCollection(DataMembersNamespace):
	def __getitem__(self, key: str) -> Any:
		try:
			value = getattr(self._instance, key)
		except AttributeError:
			raise KeyError(key)
		if inspect.ismethod(value):
			raise KeyError(key)
		return value
