
from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, Any
if TYPE_CHECKING:
    from typing import Mapping
    from ..http.response import Response
    from .token import Token

import re

from ..exceptions import ArgExcMixin

class ArgExc(ArgExcMixin):
    pass


class UnknownTokenType(ArgExc):
    def __init__(self, arg: object = None, *, token: Token):
        super().__init__(arg)
        self.token: Token = token

class OAuth2ResponseError(ArgExc):
    """
    As detailed in the OAuth2 spec. For more information see
    https://tools.ietf.org/html/rfc6749#section-5.2
    """
    ERROR_NAME: ClassVar[str] = ''

    def __init__(self, arg: object = None, *,
            error_name: str = '',
            description: str = '',
            help_uri: str = '') -> None:
        super().__init__(arg)
        self.error_name: str = error_name
        self.description: str = description
        self.help_uri: str = help_uri

    def get_default_message(self) -> str:
        if self.description:
            return repr(self.description)
        return ''

class TokenServerResponseError(OAuth2ResponseError):
    pass

class TokenServerResponseErrorTypes:
    class InvalidRequest(TokenServerResponseError):
        ERROR_NAME = 'invalid_request'

    class InvalidClient(TokenServerResponseError):
        ERROR_NAME = 'invalid_client'

    class InvalidGrant(TokenServerResponseError):
        ERROR_NAME = 'invalid_grant'

    class UnauthorizedClient(TokenServerResponseError):
        ERROR_NAME = 'unauthorized_client'

    class UnsupportedGrantType(TokenServerResponseError):
        ERROR_NAME = 'unsupported_grant_type'

    class InvalidScope(TokenServerResponseError):
        ERROR_NAME = 'invalid_scope'

class UnrecognizedTokenServerResponseError(TokenServerResponseError):
    pass

token_server_response_error_by_error_name: Mapping[str, type[TokenServerResponseError]] = {
    cls.ERROR_NAME: cls
    for cls in [
        TokenServerResponseError,
        TokenServerResponseErrorTypes.InvalidRequest,
        TokenServerResponseErrorTypes.InvalidClient,
        TokenServerResponseErrorTypes.InvalidGrant,
        TokenServerResponseErrorTypes.UnauthorizedClient,
        TokenServerResponseErrorTypes.UnsupportedGrantType,
        TokenServerResponseErrorTypes.InvalidScope,
    ]
}

def raise_for_token_server_response_error(json_dict: Any) -> None:
    error_name = json_dict.get('error')
    if error_name is None:
        return

    cls = token_server_response_error_by_error_name.get(error_name, UnrecognizedTokenServerResponseError)
    raise cls(
        error_name=error_name,
        description=json_dict.get('error_description', ''),
        help_uri=json_dict.get('error_uri', ''),
    )

class ResourceServerResponseError(OAuth2ResponseError):
    pass

class ResourceServerResponseErrorTypes:
    class InvalidRequest(ResourceServerResponseError):
        ERROR_NAME = 'invalid_request'

    class InvalidToken(ResourceServerResponseError):
        ERROR_NAME = 'invalid_token'

    class InsufficientScope(ResourceServerResponseError):
        ERROR_NAME = 'insufficient_scope'

class UnrecognizedResourceServerResponseError(ResourceServerResponseError):
    pass

resource_server_response_error_by_error_name: Mapping[str, type[ResourceServerResponseError]] = {
    cls.ERROR_NAME: cls
    for cls in [
        ResourceServerResponseError,
        ResourceServerResponseErrorTypes.InvalidRequest,
        ResourceServerResponseErrorTypes.InvalidToken,
        ResourceServerResponseErrorTypes.InsufficientScope,
    ]
}

def raise_for_resource_server_response_error(json_dict: Any) -> None:
    error_name = json_dict.get('error')
    if error_name is None:
        return

    cls = resource_server_response_error_by_error_name.get(
            error_name, UnrecognizedResourceServerResponseError)
    raise cls(
        error_name=error_name,
        description=json_dict.get('error_description', ''),
        help_uri=json_dict.get('error_uri', ''),
    )

_auth_param_pattern = r'''(?P<key>(\w+))=((?P<q>\")(?P<value>([^\"]*))(?P=q)|(?P=value))'''
_auth_param_regex = re.compile(_auth_param_pattern)

def extract_www_authenticate_auth_params(resp: Response) -> Mapping[str, str]:
    try:
        www_authenticate = resp.headers['WWW-Authenticate']
    except KeyError:
        return {}

    # Parsing the WWW-Authenticate header in a RFC-2617 spec compliant way is a daunting task.
    # Just use regex for now.
    return {m['key']: m['value'] for m in _auth_param_regex.finditer(www_authenticate)}
