
from __future__ import annotations
from typing import Mapping, Any

from ..stylesheet import StylesheetInfo, StylesheetImage

def load_stylesheet_info(d: Mapping[str, Any]) -> StylesheetInfo:
    return StylesheetInfo(
        content=d['stylesheet'],
        images=[
            StylesheetImage(
                name=m['name'],
                url=m['url'],
            )
            for m in d['images']
        ],
    )
