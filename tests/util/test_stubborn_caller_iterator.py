
from redditwarp.util.stubborn_caller_iterator import StubbornCallerIterator

def test_iteration():
	it = [
		lambda: 1,
		lambda: 7,
		lambda: 2,
		lambda: 8,
		lambda: 5,
	]
	sci = StubbornCallerIterator(it)
	assert list(sci) == [1, 7, 2, 8, 5]

	assert list(StubbornCallerIterator([])) == []

def test_exception_during_iteration():
	class throw_on_first_call_then_return:
		def __init__(self):
			self.call_count = 0
		def __call__(self):
			self.call_count += 1
			if self.call_count == 1:
				raise RuntimeError
			return 3

	j = throw_on_first_call_then_return()
	it = [
		lambda: 1,
		lambda: 2,
		j,
		lambda: 4,
		lambda: 5,
	]
	sci = StubbornCallerIterator(it)
	assert next(sci) == 1
	assert next(sci) == 2
	assert sci.current is None
	try:
		next(sci)
	except RuntimeError:
		pass
	assert sci.current is j
	assert next(sci) == 3
	assert sci.current is None
	assert next(sci) == 4
	assert next(sci) == 5
