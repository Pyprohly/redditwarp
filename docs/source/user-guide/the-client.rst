
===============
Meet The Client
===============

Let's take a deeper look into what the client object is capable of.

Instantiation
-------------

The `grant` parameter
~~~~~~~~~~~~~~~~~~~~~

We've already seen
:ref:`several ways <the-client-constructor>`
of constructing a client instance by directly
inputting various combinations of credentials, but there's an important
constructor overload we haven't yet covered::

   @overload
   def __init__(self, client_id: str, client_secret: str, /, *, grant: AuthorizationGrant) -> None: ...

This overload with the `grant` keyword is the universal one; the other
overloads are shorthands for this one.

The `grant` keyword takes a mapping (`Mapping[str, str]`) of grant credentials.
There are built-in mapping object types found in :mod:`redditwarp.auth.grants`
that make expressing grant credentials cleaner. For example, the pairs of
Client instantiation lines below are functionally identical::

   from redditwarp.SYNC import Client
   from redditwarp.auth import grants

   Client(CLIENT_ID, CLIENT_SECRET)
   Client(CLIENT_ID, CLIENT_SECRET, grant=grants.ClientCredentialsGrant())

   Client(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
   Client(CLIENT_ID, CLIENT_SECRET, grant=grants.RefreshTokenGrant(REFRESH_TOKEN))

   Client(CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD)
   Client(CLIENT_ID, CLIENT_SECRET, grant=grants.ResourceOwnerPasswordCredentialsGrant(USERNAME, PASSWORD))

The need for the `grant` keyword parameter should be rare. The only practical
situation where you would want to use this parameter is if you need to use the
installed client grant type. There also happens to be little reason to ever
pass in a :class:`redditwarp.auth.grants.AuthorizationCodeGrant` grant type
since that grant type is only used as part of a more complex OAuth flow.

Since the installed client grant type is a Reddit-specified extension grant
type, the helper mapping object is located at
:class:`redditwarp.core.grants.InstalledClientGrant` instead of in
:mod:`redditwarp.auth.grants`.

::

   import uuid
   import redditwarp.core.grants as core_grants

   grant = core_grants.InstalledClientGrant(str(uuid.uuid1()))
   Client(CLIENT_ID, CLIENT_SECRET, grant=grant)

The PRAW config constructor
~~~~~~~~~~~~~~~~~~~~~~~~~~~

RedditWarp doesn't formalise or prescribe any particular file format for
storing your API credentials, but it does offer support for PRAW_'s `praw.ini`
files for convenience via
:meth:`Client.from_praw_config() <redditwarp.client_SYNC.Client.from_praw_config>`.
See :ref:`here <the-praw-ini-file>` for more info.

.. _PRAW: https://praw.readthedocs.io/en/stable/

The access token constructor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have your own way of obtaining API access tokens, a client
instance can be instantiated from one using
:meth:`Client.from_access_token() <redditwarp.client_SYNC.Client.from_access_token>`.

When the access token expires, API calls will result in a 401 Unauthorized
:class:`~redditwarp.http.exceptions.StatusCodeException` exception.
The
:meth:`Client.set_access_token() <redditwarp.client_SYNC.Client.set_access_token>`
instance method can be used to assign a new
token.

Setting a user agent
--------------------

The
:meth:`Client.set_user_agent() <redditwarp.client_SYNC.Client.set_user_agent>`
method can be used to set a user agent. The full user agent that gets used
differs slightly. The
:meth:`client.http.set_user_agent() <redditwarp.core.http_client_SYNC.HTTPClient.set_user_agent>`
function can be used to set the full user agent. However, doing so is not
advised and if not done correctly you may be in violation of the Reddit API
guidelines.

::

   >>> from redditwarp.SYNC import Client
   >>> client = Client()
   >>> client.set_user_agent("u_SuvaBot/1.0.0 (by u/Pyprohly)")
   >>> print(client.http.get_user_agent())
   RedditWarp/0.7.0 Python/3.10.6 httpx/0.23.0 Bot !-- u_SuvaBot/1.0.0 (by u/Pyprohly)

Making requests
---------------

The
:meth:`client.request() <redditwarp.client_SYNC.Client.request>`
method is the building block of all the methods in the
procedure index.

Use of this method is only really appropriate for making calls to the Reddit
API and not any other website because of the domain specific post processing
that happens with the response data.

If you do want to make requests to other websites, you are welcome to use the
:meth:`client.http.request() <redditwarp.http.http_client_SYNC.HTTPClient.request>`
method::

   >>> from redditwarp.http.util.json_loading import load_json_from_response
   >>> resp = client.http.request('GET', 'http://httpbin.org/get')
   >>> json = load_json_from_response(resp)

RedditWarp will never leak your API tokens to other websites.

Request inspection
------------------

Let's say you're curious about the underlying calls that make up a complicated
series of RedditWarp procedure calls. We can inspect the calls that RedditWarp
performed through the `client.http.last` object.

::

   >>> it = client.p.front.pull.hot(amount=220)
   >>> _ = list(it)
   >>> for xchg in client.http.last.exchange_queue:
   ...     print("{0.verb} {0.url}".format(xchg.request))
   ...
   GET https://oauth.reddit.com/hot?limit=100&raw_json=1&api_type=json
   GET https://oauth.reddit.com/hot?limit=100&count=100&after=t3_zegunl&raw_json=1&api_type=json
   GET https://oauth.reddit.com/hot?limit=20&count=200&after=t3_ze675a&raw_json=1&api_type=json

The last 16 exchanges get recorded. The last element is most recent.

The HTTP client
---------------

The RedditWarp client uses the
:class:`~redditwarp.http.http_client_SYNC.HTTPClient`
object at `client.http` to make requests.

The `HTTPClient`'s main methods are
:meth:`~redditwarp.http.http_client_SYNC.HTTPClient.request`
and
:meth:`~redditwarp.http.http_client_SYNC.HTTPClient.inquire`.
They share
the same parameters. The `request()` function simply invokes the `inquire()`
method and returns the response object.

The parameters `verb`, `url`, `params`, and `headers` are self-explanatory.
The `data` parameter is used to send URL-encoded form data,
the `json` parameter is used to send JSON data, and
the `files` parameter is used to send multipart form data.

The parameters `data`, `json`, and `files` are mutually exclusive,
although the `data` parameter can be used with `files` just as another
way of writing `files={**data, **files}`.

::

   >>> resp = client.http.request('POST', 'http://httpbin.org/post', data={'a': 'b'})
   >>> resp.ensure_successful_status()
   >>> print(resp.data.decode())
   {
     "args": {},
     "data": "",
     "files": {},
     "form": {
       "a": "b"
     },
     "headers": {
       "Accept": "*/*",
       "Accept-Encoding": "gzip, deflate",
       "Content-Length": "3",
       "Content-Type": "application/x-www-form-urlencoded",
       "Host": "httpbin.org",
       "User-Agent": "RedditWarp/0.7.0 Python/3.10.6 httpx/0.23.0 Bot !-- API testing",
       "X-Amzn-Trace-Id": "Root=1-63908f05-79dd49354966fbcb081cb9aa"
     },
     "json": null,
     "origin": "47.74.3.224",
     "url": "http://httpbin.org/post"
   }

If you want to read in JSON data you can use
`redditwarp.http.util.json_loading.load_json_from_response(resp)`
or
`json.loads(resp.data)`.

The `client.http` HTTP client can be used to send requests to domains other
than Reddit: the Reddit credentials will not be accidentally forwarded to
non-Reddit domains, nor will those requests be rate limited. On the other hand,
using the `client.http` object to make non-Reddit requests is probably not
ideal and a :doc:`separate HTTP client <http-components>` should be used instead.

The authorizer
--------------

An object called the 'authorizer' is located at
:attr:`client.http.authorizer <redditwarp.core.http_client_SYNC.RedditHTTPClient.authorizer>`.
Its role is to authorize outgoing requests and manage the access token obtained
from the token client.

The token client at
:attr:`client.http.authorizer.token_client <redditwarp.core.authorizer_SYNC.Authorizer.token_client>`
contains the logic to
fetch new access tokens from the token server. The credentials we gave to the
client constructor can be found on this object.

The :meth:`~redditwarp.core.authorizer_SYNC.Authorizer.renew_token`
method on `client.http.authorizer` is automatically
invoked the first time you make any (reddit.com directed) request through the
RedditWarp client, and it populates the
:attr:`client.http.authorizer.token <redditwarp.core.authorizer_SYNC.Authorizer.token>`
attribute which stores the API access token.

::

   >>> client.http.authorizer.token_client.client_creds
   ('cvQTsEXAMPLE9qlKflga7L', '2reTtEXAMPLE7mDAvpdg20j3P9Iqdu')
   >>> client.http.authorizer.token_client.grant
   RefreshTokenGrant(refresh_token='69268695264-IAyOnEXAMPLEkHXsdi9aMdULbIvFJi', scope=None)
   >>> assert client.http.authorizer.token is None
   >>> client.http.authorizer.renew_token()
   >>> client.http.authorizer.token
   Token(access_token='10706140460-h5ErvEXAMPLE4eEmbcwifLnIOCY7hQ', token_type='bearer', expires_in=86400, refresh_token='69268695264-IAyOnEXAMPLEkHXsdi9aMdULbIvFJi', scope='*')
   >>> client.http.authorizer.token.access_token
   '10706140460-h5ErvEXAMPLE4eEmbcwifLnIOCY7hQ'
