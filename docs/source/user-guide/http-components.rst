
===============
HTTP Components
===============

RedditWarp does not commit to a specific HTTP transport library but instead
contains adapters to support a variety of them. These adapters can be used in
your own programs to make them HTTP transport library agnostic.

It is important to note that the functionality of RedditWarp's HTTP library is
limited in scope and does not have advanced features such as cookie handling,
HTTP/2 support, the ability to set custom headers on multipart fields, or
streaming capabilities.

The HTTP components can be found under :mod:`redditwarp.http`.
The design of these components were inspired by the `System.Net.Http`
package of C#.NET.

-------------------------------------------------

Main components:

* :class:`~redditwarp.http.http_client_SYNC.HTTPClient`

  A class used to make web requests.

  The main methods are :meth:`~redditwarp.http.http_client_SYNC.HTTPClient.request`,
  :meth:`~redditwarp.http.http_client_SYNC.HTTPClient.request`,
  and :meth:`~redditwarp.http.http_client_SYNC.HTTPClient.submit`.
  These methods perform similar functions and delegate to each other.
  Both `request()` and `inquire()` take the same parameters, with
  `request()` delegating to `inquire()` and returning the response from the
  `Exchange` object. The `inquire()` method creates a `Requisition` object and
  passes it to `submit()`.

  The parameters `verb`, `url`, `params`, and `headers` are self-explanatory.
  The `data` parameter is used to send URL-encoded form data,
  the `json` parameter is used to send JSON data, and
  the `files` parameter is used to send multipart form data.

  The parameters `data`, `json`, and `files` are mutually exclusive,
  although the `data` parameter can be used with `files` just as another
  way of writing `files={**data, **files}`.

  The `HTTPClient` constructor takes a `Handler` object.

* :class:`~redditwarp.http.exchange.Exchange`

  A class returned by the `HTTPClient.inquire()` method that contains information
  about the request and response.

* :class:`~redditwarp.http.requisition.Requisition`

  This object represents a request for an outgoing request.
  It is designed to be modified by the handlers in a handler chain.
  You can construct a `Requisition` object
  yourself and pass it to the `HTTPClient.submit()` method.

Handers:

* :class:`~redditwarp.http.handler_SYNC.Handler`

  A base class. The `HTTPClient` constructor takes a `Handler` object.

* :class:`~redditwarp.http.delegating_handler_SYNC.DelegatingHandler`

  A class allowing a handler to be used as a component in a handler chain.

* :class:`~redditwarp.http.transport.connector_SYNC.Connector`

  A handler class that operates at the end of a handler chain and performs the
  HTTP request. These classes are the HTTP transport library adaptors.

-------------------------------------------------

An `HTTPClient` object must be constructed to make requests.
Pass a `Connector` object to `HTTPClient` to construct it::

   from redditwarp.http.transport.auto_SYNC import new_connector
   from redditwarp.http.http_client_SYNC import HTTPClient

   http = HTTPClient(new_connector())

Making requests
---------------

::

   resp = http.request('GET', 'http://httpbin.org/get')
   # OR
   resp = http.inquire('GET', 'http://httpbin.org/get').response

   print(resp.data.decode())

If we don't want to specify the base URL each time, the `HTTPClient.base_url`
attribute can be set.

::

   http.base_url = 'http://httpbin.org'
   resp = http.request('GET', '/get')
   resp = http.request('POST', '/post')
   resp = http.request('DELETE', '/delete')

Use the `inquire()` method to get information about the actual request as
well.

::

   xchg = http.inquire('GET', '/get')
   requ = xchg.request
   resp = xchg.response

Sending params
--------------

::

   >>> requ = http.inquire('GET', 'http://httpbin.org/get', params={'a': '1', 'b': '2'}).request
   >>> requ.url
   'http://httpbin.org/get?a=1&b=2'

The `params` mapping must only contain strings.

Sending headers
---------------

::

   >>> requ = http.inquire('GET', 'http://httpbin.org/get').request
   >>> requ.headers['User-Agent']
   'python-httpx/0.23.0'
   >>> requ = http.inquire('GET', 'http://httpbin.org/get', headers={'User-Agent': 'my-app/0.1.0'}).request
   >>> requ.headers['User-Agent']
   'my-app/0.1.0'
   >>> requ.headers['uSeR-agENT']
   'my-app/0.1.0'

Sending headers is just like sending parameters. However, whenever you see a
`header` field on an object you can assume that it is a case-insensitive
mapping.

Sending URL-encoded form data
-----------------------------

Use the `data` parameter.
Again, the contents of the mapping must be only strings.

::

   >>> requ = http.inquire('POST', 'http://httpbin.org/post', data={'a': '1', 'b': '2'}).request
   >>> requ.data
   b'a=1&b=2'

Sending JSON
------------

Use the `json` parameter.

::

   >>> requ = http.inquire('POST', 'http://httpbin.org/post', json={'a': [1, 2, 3]}).request
   >>> requ.data
   b'{"a": [1, 2, 3]}'

Sending files
-------------

Use the `files` parameter to send media data via multipart form data.

::

   >>> files = {'file': open('file1', 'rb')}
   >>> requ = http.inquire('POST', 'http://httpbin.org/post', files=files).request
   >>> requ.data
   b'--9055dc7b5eda1da2b214831aae84aaa7\r\nContent-Disposition: form-data; name="file"\r\nContent-Type: application/octet-stream\r\n\r\nhi\r\n--9055dc7b5eda1da2b214831aae84aaa7--\r\n'

Binary response content
-----------------------

The response content can be accessed as bytes through the `data` attribute of
the response object.

::

   resp = http.request('GET', 'http://httpbin.org/get', data={'hello': 'world'})
   print(resp.data.decode())

JSON response content
---------------------

JSON can be extracted manually with `json.loads()`, or using the
:func:`~redditwarp.http.util.json_loading.load_json_from_response`
utility function on a `Response` object:

::

   resp = http.request('GET', 'http://httpbin.org/get', data={'hello': 'world'})
   from redditwarp.http.util.json_loading import load_json_from_response
   json = load_json_from_response(resp)
   print(json)

Response status code
--------------------

The response status code is available though the `status` attribute on a
`Response` object.

The :meth:`~redditwarp.http.response.Response.ensure_successful_status`
method will raise a
:exc:`redditwarp.http.exceptions.StatusCodeException`
for status codes not in the 2XX range.

::

   >>> resp = http.request('GET', 'http://httpbin.org/status/404')
   >>> resp.status
   404
   >>> resp.ensure_successful_status()
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "/Users/danpro/Desktop/redditwarp/redditwarp/http/response.py", line 31, in ensure_successful_status
       ensure_successful_status(self.status)
     File "/Users/danpro/Desktop/redditwarp/redditwarp/http/exceptions.py", line 124, in ensure_successful_status
       raise_now(n)
     File "/Users/danpro/Desktop/redditwarp/redditwarp/http/exceptions.py", line 119, in raise_now
       raise get_status_code_exception_class_by_status_code(n)(status_code=n)
   redditwarp.http.exceptions.StatusCodeExceptionTypes.NotFound: 404 Not Found

Timeouts
--------

A default timeout can be set on an `HTTPClient` instance using the
:attr:`~redditwarp.http.http_client_SYNC.HTTPClient.timeout`
attribute. It is `100` seconds by default.

Timeouts can be specified per request using the `timeout` parameter. A value of
`-1` means an infinite timeout. A value of `-2`, which is the default,
tells the HTTPClient to use the `HTTPClient.timeout` instance value.

::

   http.request('GET', 'https://google.com/', timeout=0.0000001)
