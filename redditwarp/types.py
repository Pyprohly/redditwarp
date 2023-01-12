
from typing import Union, Mapping, Sequence, Dict, List

# https://github.com/python/typing/issues/182#issuecomment-1320974824
JSON = Union[Dict[str, 'JSON'], List['JSON'], str, int, float, bool, None]
JSON_ro = Union[Mapping[str, 'JSON_ro'], Sequence['JSON_ro'], str, int, float, bool, None]
