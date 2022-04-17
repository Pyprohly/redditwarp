
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .token import Token

from ...exceptions import ArgExcMixin

class ArgExc(ArgExcMixin):
    pass


class UnknownTokenType(ArgExc):
    def __init__(self, arg: object = None, *, token: Token):
        super().__init__(arg)
        self.token: Token = token

class RedditInternalAPITokenServerResponseError(ArgExc):
    def __init__(self, arg: object = None, *,
            codename: str = '',
            explanation: str = '') -> None:
        super().__init__(arg)
        self.codename: str = codename
        self.explanation: str = explanation

    def get_default_message(self) -> str:
        co = self.codename
        xp = self.explanation
        if co:
            if xp:
                return f'{co}: {xp}'
            return co
        return ''

def raise_for_token_server_response_error(json_dict: Any) -> None:
    if json_dict.get('success', True):
        return

    error = json_dict['error']
    raise RedditInternalAPITokenServerResponseError(
        codename=error.get('reason') or '',
        explanation=error.get('explanation') or '',
    )
