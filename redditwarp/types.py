
from typing import Union, Mapping, Sequence

# https://github.com/python/typing/issues/182#issuecomment-1320974824
JSON = Union[dict[str, 'JSON'], list['JSON'], str, int, float, bool, None]
JSON_ro = Union[Mapping[str, 'JSON_ro'], Sequence['JSON_ro'], str, int, float, bool, None]
