
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .token import Token

from ...exceptions import ArgExcMixin

class ArgExc(ArgExcMixin):
    pass


class UnknownTokenType(ArgExc):
    def __init__(self, arg: object = None, *, token: Token) -> None:
        super().__init__(arg)
        self.token: Token = token
        ("")

class TokenServerResponseError(ArgExc):
    def __init__(self, arg: object = None, *,
            label: str = '',
            explanation: str = '') -> None:
        super().__init__(arg)
        self.label: str = label
        ("")
        self.explanation: str = explanation
        ("")

    def get_default_message(self) -> str:
        la = self.label
        xp = self.explanation
        if la:
            if xp:
                return f'{la}: {xp}'
            return la
        return ''

def raise_for_token_server_response_error(json_dict: Any) -> None:
    if json_dict.get('success', True):
        return

    error = json_dict['error']
    raise TokenServerResponseError(
        label=error.get('reason') or '',
        explanation=error.get('explanation') or '',
    )
