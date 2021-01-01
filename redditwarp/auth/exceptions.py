
from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar, Any
if TYPE_CHECKING:
    from typing import Mapping
    from ..http.response import Response

import re

from .. import http
from ..exceptions import ArgInfoExceptionMixin

class RootException(Exception):
    pass

class ArgInfoException(ArgInfoExceptionMixin, RootException):
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

class UnrecognizedOAuth2ResponseError(ResponseException):
    pass

class OAuth2ResponseError(ResponseException):
    """
    As detailed in the OAuth2 spec. For more information see
    https://tools.ietf.org/html/rfc6749#section-5.2
    """
    ERROR_NAME: ClassVar[str] = ''

    def __init__(self, arg: object = None, *, response: Response, error_name: str = '',
            description: str = '', help_uri: str = '') -> None:
        super().__init__(arg=arg, response=response)
        self.error_name = error_name
        self.description = description
        self.help_uri = help_uri

    def get_default_message(self) -> str:
        if self.description:
            return repr(self.description)
        return ''

class InvalidRequest(OAuth2ResponseError):
    ERROR_NAME = 'invalid_request'

class InvalidClient(OAuth2ResponseError):
    ERROR_NAME = 'invalid_client'

class InvalidGrant(OAuth2ResponseError):
    ERROR_NAME = 'invalid_grant'

class UnauthorizedClient(OAuth2ResponseError):
    ERROR_NAME = 'unauthorized_client'

class UnsupportedGrantType(OAuth2ResponseError):
    ERROR_NAME = 'unsupported_grant_type'

class InvalidScope(OAuth2ResponseError):
    ERROR_NAME = 'invalid_scope'

class InvalidToken(OAuth2ResponseError):
    ERROR_NAME = 'invalid_token'

class InsufficientScope(OAuth2ResponseError):
    ERROR_NAME = 'insufficient_scope'

oauth2_response_error_class_by_error_name = {
    cls.ERROR_NAME: cls
    for cls in [
        OAuth2ResponseError,
        InvalidRequest,
        InvalidClient,
        InvalidGrant,
        UnauthorizedClient,
        UnsupportedGrantType,
        InvalidScope,
        InvalidToken,
        InsufficientScope,
    ]
}

def raise_for_oauth2_response_error(resp: Response, json_dict: Any) -> None:
    error_name = json_dict.get('error')
    if error_name is None:
        return
    cls = oauth2_response_error_class_by_error_name.get(error_name)
    if cls is None:
        raise UnrecognizedOAuth2ResponseError(response=resp)
    raise cls(
        response=resp,
        error_name=json_dict.get('error', ''),
        description=json_dict.get('error_description', ''),
        help_uri=json_dict.get('error_uri', ''),
    )

def raise_for_token_server_response(resp: Response, json_dict: Any) -> None:
    raise_for_oauth2_response_error(resp, json_dict)

def raise_for_reddit_token_server_response(resp: Response, json_dict: Any) -> None:
    error = json_dict.get('error')
    if not isinstance(error, str):
        return
    raise_for_token_server_response(resp, json_dict)

_www_authenticate_auth_param_regex = re.compile(r'(\w+)=\"(.*?)\"')

def raise_for_resource_server_response(resp: Response) -> None:
    try:
        www_authenticate: str = resp.headers['WWW-Authenticate']
    except KeyError:
        return
    m: Mapping[str, str] = dict(_www_authenticate_auth_param_regex.findall(www_authenticate))
    raise_for_oauth2_response_error(resp, m)
