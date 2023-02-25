
from typing import Mapping, Union, IO, Tuple

RequestFiles = Mapping[str, Union[str, IO[bytes]]]
ExtendedRequestFiles = Mapping[
    str,
    Union[
        str,
        IO[bytes],
        Tuple[IO[bytes], str],
        Tuple[IO[bytes], str, str],
    ],
]
