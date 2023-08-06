
from __future__ import annotations
from typing import TypeVar, Iterable, Iterator, Tuple

import pytest

from redditwarp.util.token_bucket import TokenBucket

T = TypeVar('T')

class CallIterator(Iterator[T]):
    """Get next item by calling the iterator."""
    def __init__(self, iterable: Iterable[T]) -> None:
        self._iterator = iter(iterable)
    def __iter__(self) -> Iterator[T]:
        return self
    def __next__(self) -> T:
        return next(self._iterator)
    def __call__(self) -> T:
        return next(self)

'''
import random
samples = 9
for _ in range(samples):
    capacity = random.uniform(1, 50)
    rate = random.uniform(1, capacity)
    rounds = 2
    time_values = sorted(random.uniform(1, 15) for _ in range(1 + 2*rounds))
    ci = CallIterator(time_values)
    tb = TokenBucket(capacity, rate, ci)
    concomitants = []
    for _ in range(rounds):
        m = random.uniform(1, 7)
        _ = tb.try_consume(m)
        n = tb.get_value()
        concomitants.append((m, n))
    print((capacity, rate, time_values, concomitants))
'''
@pytest.mark.parametrize(
    "capacity, rate, time_values, concomitants",
    (
        (32.24905487371517, 1.6782744028143597, [1.9114045994040454, 6.969037867426095, 9.857047493522815, 10.633052016407657, 11.712740424483197], [(5.995549680733708, 32.24905487371517), (5.323419682361689, 31.772507821913074)]),
        (36.182817389917524, 26.842859421842405, [3.2353720580986707, 4.72991984015909, 8.95680567771927, 9.936813508593648, 13.750569243961213], [(4.129635178823713, 36.182817389917524), (4.1007763324671345, 36.182817389917524)]),
        (1.1678140988438948, 1.0248759000283574, [1.7343536676707396, 2.0623887862463017, 4.902816135217915, 8.938958020469325, 14.958534217659619], [(3.5921934448188657, 1.1678140988438948), (1.9269604838834795, 1.1678140988438948)]),
        (1.9593554404567093, 1.2512112291940607, [4.362148240644381, 8.69325278485655, 9.63262779512963, 9.948854189053721, 13.356463553510197], [(3.3722619932432876, 1.9593554404567093), (3.11262624682879, 1.9593554404567093)]),
        (14.016048624112596, 2.861890381627925, [2.768870739506374, 4.308506982965525, 10.256306408319151, 12.40731838021447, 12.800890465279103], [(1.3614481373317635, 14.016048624112596), (6.228929752077063, 14.016048624112596)]),
        (9.698961318240302, 7.5934311698067845, [4.775436404804642, 6.09066690560283, 9.654383400007365, 11.44707198001736, 13.626531481638201], [(3.863118371226456, 9.698961318240302), (1.438700831769363, 9.698961318240302)]),
        (31.544524342766845, 15.142118084893482, [3.2361243140165428, 3.9547675422136224, 6.02200990254164, 6.466178700936169, 9.254650905530138], [(3.327774952277884, 31.544524342766845), (1.7676380648843792, 31.544524342766845)]),
        (22.07204410014468, 2.7205455999633967, [1.821831427021423, 5.098416469275915, 6.397047030095505, 7.907115771354322, 14.728017710205934], [(2.1213042788164813, 22.07204410014468), (3.2686385729858696, 22.07204410014468)]),
        (17.908253226817134, 11.762644890533657, [4.280799532715026, 5.308715992454407, 6.31548824844403, 8.711832080993767, 13.522405902436892], [(3.8420594231178264, 17.908253226817134), (4.379489608785382, 17.908253226817134)]),
    )
)
def test_get_value(
    capacity: float,
    rate: float,
    time_values: Iterable[float],
    concomitants: Iterable[Tuple[float, float]],
) -> None:
    ci = CallIterator(time_values)
    tb = TokenBucket(capacity, rate, time_func=ci)
    assert tb.get_value() == capacity
    for m, n in concomitants:
        tb.try_consume(m)
        assert tb.get_value() == pytest.approx(n)

def test_negative_consume_values_dont_cause_the_bucket_to_exceed_capacity() -> None:
    tb = TokenBucket(capacity=10, rate=1)
    tb.try_consume(-5)
    tb.consume(-5)
    tb.hard_consume(-5)
    assert tb.get_value() == 10
