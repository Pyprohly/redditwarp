
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, ClassVar
if TYPE_CHECKING:
    from typing import Iterator, Optional

from dataclasses import dataclass, field

@dataclass(frozen=True)
class AuthorizationGrant(Mapping[str, str]):
    """A class to construct authorization grant mappings conveniently.

    An authorization grant is a credential representing the resource
    owner's authorization that's used to exchange for a bearer token.

    An empty string should be treated the same as `None` in all fields
    annotated as `Optional`. The annotations reflect the field value
    requirements of the various grants types defined in the OAuth2 spec.
    """
    GRANT_TYPE: ClassVar[str] = ''
    _d: dict[str, str] = field(init=False, repr=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._d['grant_type'] = self.GRANT_TYPE
        self._d.update({
            k: v
            for k, v in vars(self).items()
            if not k.startswith('_')
            if v
        })

    def __contains__(self, item: object) -> bool:
        return item in self._d
    def __iter__(self) -> Iterator[str]:
        return iter(self._d)
    def __len__(self) -> int:
        return len(self._d)
    def __getitem__(self, key: str) -> str:
        return self._d[key]

@dataclass(frozen=True)
class AuthorizationCodeGrant(AuthorizationGrant):
    GRANT_TYPE: ClassVar[str] = 'authorization_code'
    code: str
    redirect_uri: Optional[str]
    client_id: Optional[str] = None

@dataclass(frozen=True)
class ResourceOwnerPasswordCredentialsGrant(AuthorizationGrant):
    GRANT_TYPE: ClassVar[str] = 'password'
    username: str
    password: str
    scope: Optional[str] = None

@dataclass(frozen=True)
class ClientCredentialsGrant(AuthorizationGrant):
    GRANT_TYPE: ClassVar[str] = 'client_credentials'
    scope: Optional[str] = None

@dataclass(frozen=True)
class RefreshTokenGrant(AuthorizationGrant):
    GRANT_TYPE: ClassVar[str] = 'refresh_token'
    refresh_token: str
    scope: Optional[str] = None
