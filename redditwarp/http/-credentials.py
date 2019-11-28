"""OAuth 2.0 Credentials."""

from .auth import credentials

class Credentials(credentials.Credentials):
	"""Credentials using OAuth 2.0 access and refresh tokens."""
















    def __init__(self, token, refresh_token=None, id_token=None,
                 token_uri=None, client_id=None, client_secret=None,
                 scopes=None):
        """
        Args:
            token (Optional(str)): The OAuth 2.0 access token. Can be None
                if refresh information is provided.
            refresh_token (str): The OAuth 2.0 refresh token. If specified,
                credentials can be refreshed.
            id_token (str): The Open ID Connect ID Token.
            token_uri (str): The OAuth 2.0 authorization server's token
                endpoint URI. Must be specified for refresh, can be left as
                None if the token can not be refreshed.
            client_id (str): The OAuth 2.0 client ID. Must be specified for
                refresh, can be left as None if the token can not be refreshed.
            client_secret(str): The OAuth 2.0 client secret. Must be specified
                for refresh, can be left as None if the token can not be
                refreshed.
            scopes (Sequence[str]): The scopes used to obtain authorization.
                This parameter is used by :meth:`has_scopes`. OAuth 2.0
                credentials can not request additional scopes after
                authorization. The scopes must be derivable from the refresh
                token if refresh information is provided (e.g. The refresh
                token scopes are a superset of this or contain a wild card
                scope like 'https://www.googleapis.com/auth/any-api').
        """
        super(Credentials, self).__init__()
        self.token = token
        self._refresh_token = refresh_token
        self._id_token = id_token
        self._scopes = scopes
        self._token_uri = token_uri
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def refresh_token(self):
        """Optional[str]: The OAuth 2.0 refresh token."""
        return self._refresh_token

    @property
    def token_uri(self):
        """Optional[str]: The OAuth 2.0 authorization server's token endpoint
        URI."""
        return self._token_uri

    @property
    def id_token(self):
        """Optional[str]: The Open ID Connect ID Token.
        Depending on the authorization server and the scopes requested, this
        may be populated when credentials are obtained and updated when
        :meth:`refresh` is called. This token is a JWT. It can be verified
        and decoded using :func:`google.oauth2.id_token.verify_oauth2_token`.
        """
        return self._id_token

    @property
    def client_id(self):
        """Optional[str]: The OAuth 2.0 client ID."""
        return self._client_id

    @property
    def client_secret(self):
        """Optional[str]: The OAuth 2.0 client secret."""
        return self._client_secret

    @property
    def requires_scopes(self):
        """False: OAuth 2.0 credentials have their scopes set when
        the initial token is requested and can not be changed."""
        return False

    @_helpers.copy_docstring(credentials.Credentials)
    def refresh(self, request):
        if (self._refresh_token is None or
                self._token_uri is None or
                self._client_id is None or
                self._client_secret is None):
            raise exceptions.RefreshError(
                'The credentials do not contain the necessary fields need to '
                'refresh the access token. You must specify refresh_token, '
                'token_uri, client_id, and client_secret.')

        access_token, refresh_token, expiry, grant_response = (
            _client.refresh_grant(
                request, self._token_uri, self._refresh_token, self._client_id,
                self._client_secret, self._scopes))

        self.token = access_token
        self.expiry = expiry
        self._refresh_token = refresh_token
        self._id_token = grant_response.get('id_token')

        if self._scopes and 'scopes' in grant_response:
            requested_scopes = frozenset(self._scopes)
            granted_scopes = frozenset(grant_response['scopes'].split())
            scopes_requested_but_not_granted = (
                requested_scopes - granted_scopes)
            if scopes_requested_but_not_granted:
                raise exceptions.RefreshError(
                    'Not all requested scopes were granted by the '
                    'authorization server, missing scopes {}.'.format(
                        ', '.join(scopes_requested_but_not_granted)))
