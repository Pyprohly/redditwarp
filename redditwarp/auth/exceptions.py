
from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, Any
if TYPE_CHECKING:
    from typing import Mapping
    from ..http.response import Response

from urllib.request import parse_http_list, parse_keqv_list

from .. import http
from ..exceptions import ArgInfoExceptionMixin
from ..http.util.case_insensitive_dict import CaseInsensitiveDict

class ArgInfoException(ArgInfoExceptionMixin):
    pass


class ResponseException(ArgInfoException):
    def __init__(self, arg: object = None, *, response: Response) -> None:
        super().__init__(arg)
        self.response = response

    def get_default_message(self) -> str:
        return str(self.response)

class HTTPStatusError(ResponseException):
    pass

def raise_for_status(resp: Response) -> None:
    try:
        resp.raise_for_status()
    except http.exceptions.StatusCodeException as e:
        raise HTTPStatusError(response=resp) from e


class ResponseContentError(ResponseException):
    pass


class OAuth2ResponseError(ResponseException):
    """
    As detailed in the OAuth2 spec. For more information see
    https://tools.ietf.org/html/rfc6749#section-5.2
    """
    ERROR_NAME: ClassVar[str] = ''

    def __init__(self, arg: object = None, *, response: Response,
            error_name: str = '',
            description: str = '',
            help_uri: str = '') -> None:
        super().__init__(arg=arg, response=response)
        self.error_name = error_name
        self.description = description
        self.help_uri = help_uri

    def get_default_message(self) -> str:
        if self.description:
            return repr(self.description)
        return ''


class TokenServerResponseError(OAuth2ResponseError):
    pass

class TokenServerResponseErrors:
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

token_server_response_error_by_error_name = {
    cls.ERROR_NAME: cls
    for cls in [
        TokenServerResponseError,
        TokenServerResponseErrors.InvalidRequest,
        TokenServerResponseErrors.InvalidClient,
        TokenServerResponseErrors.InvalidGrant,
        TokenServerResponseErrors.UnauthorizedClient,
        TokenServerResponseErrors.UnsupportedGrantType,
        TokenServerResponseErrors.InvalidScope,
    ]
}

def raise_for_token_server_response_error(resp: Response, json_dict: Any) -> None:
    error_name = json_dict.get('error')
    if error_name is None:
        return

    cls = token_server_response_error_by_error_name.get(
            error_name, UnrecognizedTokenServerResponseError)
    raise cls(
        response=resp,
        error_name=error_name,
        description=json_dict.get('error_description', ''),
        help_uri=json_dict.get('error_uri', ''),
    )

def raise_for_reddit_token_server_response_error(resp: Response, json_dict: Any) -> None:
    error = json_dict.get('error')
    if not isinstance(error, str):
        return
    raise_for_token_server_response_error(resp, json_dict)


class ResourceServerResponseError(OAuth2ResponseError):
    pass

class ResourceServerResponseErrors:
    class InvalidRequest(ResourceServerResponseError):
        ERROR_NAME = 'invalid_request'

    class InvalidToken(ResourceServerResponseError):
        ERROR_NAME = 'invalid_token'

    class InsufficientScope(ResourceServerResponseError):
        ERROR_NAME = 'insufficient_scope'

class UnrecognizedResourceServerResponseError(ResourceServerResponseError):
    pass

resource_server_response_error_by_error_name = {
    cls.ERROR_NAME: cls
    for cls in [
        ResourceServerResponseError,
        ResourceServerResponseErrors.InvalidToken,
        ResourceServerResponseErrors.InsufficientScope,
    ]
}

def raise_for_resource_server_response_error(resp: Response, json_dict: Any) -> None:
    error_name = json_dict.get('error')
    if error_name is None:
        return

    cls = resource_server_response_error_by_error_name.get(
            error_name, UnrecognizedResourceServerResponseError)
    raise cls(
        response=resp,
        error_name=error_name,
        description=json_dict.get('error_description', ''),
        help_uri=json_dict.get('error_uri', ''),
    )

def parse_www_authenticate(val: str) -> Mapping[str, Mapping[str, str]]:
    # https://datatracker.ietf.org/doc/html/rfc7235#section-4.1
    dct: dict[str, list[str]] = {}
    lst: list[str] = []
    for strng in parse_http_list(val):
        left, _, right = strng.partition(' ')
        if '=' in left:
            lst.append(strng)
        else:
            lst = dct[left] = []
            lst.append(right)
    return CaseInsensitiveDict({
        k: CaseInsensitiveDict(parse_keqv_list(v))
        for k, v in dct.items()
    })

def extract_www_authenticate_bearer_auth_params(resp: Response) -> Mapping[str, str]:
    try:
        www_authenticate = resp.headers['WWW-Authenticate']
    except KeyError:
        return {}
    return parse_www_authenticate(www_authenticate)['Bearer']
