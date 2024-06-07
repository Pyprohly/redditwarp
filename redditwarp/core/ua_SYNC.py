
from __future__ import annotations
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from types import ModuleType

import sys

from .. import __about__
from ..http.transport.reg_SYNC import get_transport_adapter_module_name_and_version


_py_ver = sys.version.split(None, 1)[0]


def get_suitable_user_agent(transport_adapter_module: Union[str, ModuleType]) -> str:
    return ' '.join([
        f"{__about__.__title__}/{__about__.__version__}",
        f"Python/{_py_ver}",
        '/'.join(get_transport_adapter_module_name_and_version(transport_adapter_module)),
    ])
