
from redditwarp.util.obstinate_call_chunk_chaining_iterator import ObstinateCallChunkChainingIterator

def test_call_chunks_attrib():
	it = [lambda: [1]]
	cci = ObstinateCallChunkChainingIterator(it)
	assert cci.call_chunks is it

def test_simple_iteration():
	it = [
		lambda: [1],
		lambda: [2, 3],
		lambda: [4, 5, 6],
	]
	cci = ObstinateCallChunkChainingIterator(it)
	assert list(cci) == [1,2,3,4,5,6]

def test_current_iter():
	l1 = [0, 1, 2]
	l2 = [3, 4]
	c1 = lambda: l1
	c2 = lambda: l2
	it = [c1, c2]
	cci = ObstinateCallChunkChainingIterator(it)

	assert next(cci) == 0
	assert list(cci.current_iter) == [1, 2]
	assert next(cci) == 3
	assert next(cci) == 4

	cci.current_iter = iter((8, 9))
	assert next(cci) == 8
	assert next(cci) == 9

def test_exception_during_iteration():
	class throw_on_first_call_then_return:
		def __init__(self):
			self.call_count = 0
		def __call__(self):
			self.call_count += 1
			if self.call_count == 1:
				raise RuntimeError
			return [2]

	j = throw_on_first_call_then_return()
	it = [
		lambda: [1],
		j,
		lambda: [3],
	]
	cci = ObstinateCallChunkChainingIterator(it)
	assert cci.current_callable is None
	assert next(cci) == 1
	assert cci.current_callable is None
	try:
		next(cci)
	except RuntimeError:
		pass
	assert cci.current_callable is j
	assert next(cci) == 2
	assert cci.current_callable is None
	assert next(cci) == 3

def test_current_callable_is_setable():
	cci = ObstinateCallChunkChainingIterator(())
	assert list(cci) == []
	cci.current_callable = lambda: (1,2,3)
	assert list(cci) == [1,2,3]
