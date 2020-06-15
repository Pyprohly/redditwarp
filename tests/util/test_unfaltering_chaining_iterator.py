
from redditwarp.util.unfaltering_chaining_iterator import UnfalteringChainingIterator

def test_simple_iteration():
	it = [[62, 43, 13], [12, 38]]
	uci = UnfalteringChainingIterator(it)
	assert list(uci) == [62, 43, 13, 12, 38]
	assert list(UnfalteringChainingIterator(())) == []

def test_current_iter():
	it = [[62, 43, 13], [12, 38]]
	uci = UnfalteringChainingIterator(it)
	assert next(uci) == 62
	assert list(uci.current_iter) == [43, 13]
	assert next(uci) == 12
	assert list(uci.current_iter) == [38]
	uci.current_iter = (77,)
	assert list(uci.current_iter) == [77]

def test_exception_during_iteration():
	class throw_on_first_call_then_return:
		def __init__(self):
			self.call_count = 0
		def __iter__(self):
			self.call_count += 1
			if self.call_count == 1:
				raise RuntimeError
			yield from (-2, -3)

	j = throw_on_first_call_then_return()
	it = [
		(0, 1),
		j,
		(4, 5),
	]
	uci = UnfalteringChainingIterator(it)
	assert next(uci) == 0
	assert next(uci) == 1
	try:
		next(uci)
	except RuntimeError:
		pass
	assert next(uci) == 4
	assert next(uci) == 5
