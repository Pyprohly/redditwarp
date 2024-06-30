
============
Installation
============

RedditWarp requires a minimum Python runtime version of 3.8+.
Type annotations may use 3.9 features.
Code examples in documentation will assume 3.10.

Install/update::

   $ pip install -U redditwarp

Check that the import works in a Python REPL.

.. parsed-literal::

   >>> import redditwarp
   >>> redditwarp.__version__
   '|release|'

Install an HTTP library
-----------------------

RedditWarp has no dependencies. It will go as far as using Python's built-in
`urllib.request` module to make requests if a better HTTP transport library
isn't available. For async code, if no HTTP transport library is installed then
a `ModuleNotFoundError` exception will be raised when attempting to construct a
client instance.

The supported HTTP libraries are as follows, in order of precedence in which
RedditWarp will look for them:

* Sync:

  * HTTPX -- `<https://www.python-httpx.org/>`_
  * Requests -- `<https://requests.readthedocs.io/>`_
  * urllib3 -- `<https://urllib3.readthedocs.io/>`_
  * Python urllib.request -- `<https://docs.python.org/3/library/urllib.request.html>`_

* Async:

  * HTTPX -- `<https://www.python-httpx.org/>`_
  * AIOHTTP -- `<https://docs.aiohttp.org/en/stable/>`_

The recommended HTTP transport library is HTTPX.

::

   $ pip install -U httpx

Selecting an HTTP library
-------------------------

If you have multiple HTTP libraries installed and want to force your
program to use a specific one, such as the Requests package, add the following
code to your program's `__main__` module::

   import redditwarp.http.transport.SYNC, redditwarp.http.transport.impls.requests
   redditwarp.http.transport.SYNC.set_transport_adapter_module(redditwarp.http.transport.impls.requests)

If the HTTP library isn't installed, a `ModuleNotFoundError` exception will be
raised upon importing the transport adaptor module, in this case,
`redditwarp.http.transport.impls.requests`.
