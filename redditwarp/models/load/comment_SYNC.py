
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..comment_SYNC import (
    Variant0Comment,
    Variant1Comment,
    Variant2Comment,
)

def load_variant0_comment(d: Mapping[str, Any], client: Client) -> Variant0Comment:
    return Variant0Comment(d, client)

def load_variant1_comment(d: Mapping[str, Any], client: Client) -> Variant1Comment:
    return Variant1Comment(d, client)

def load_variant2_comment(d: Mapping[str, Any], client: Client) -> Variant2Comment:
    return Variant2Comment(d, client)
