
from __future__ import annotations
from typing import Any, Mapping, Iterator

class Document(Mapping[str, Any]):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d

    def __contains__(self, item: object) -> bool:
        return item in self.d
    def __iter__(self) -> Iterator[str]:
        return iter(self.d)
    def __len__(self) -> int:
        return len(self.d)
    def __getitem__(self, key: str) -> Any:
        return self.d[key]
