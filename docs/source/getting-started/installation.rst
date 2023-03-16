
============
Installation
============

RedditWarp requires a minimum Python runtime version of 3.8+.
Type annotations may use 3.9 features.
Code examples in documentation will assume 3.10.

Install/update::

   $ pip install -U redditwarp

Check that the import works in a Python REPL.

::

   >>> import redditwarp
   >>> redditwarp.__version__
   '1.0.0'

Install an HTTP library
-----------------------

RedditWarp has no dependencies. It will go as far as using Python's built-in
`urllib.request` module to make requests if a better HTTP transport library
isn't available. For async code, if no HTTP transport library is installed then
an `ModuleNotFoundError` exception will be raised when attempting to construct a
client instance.

The supported HTTP libraries are as follows, in order of precedence:

Sync:

* HTTPX -- `<https://www.python-httpx.org/>`_
* Requests -- `<https://requests.readthedocs.io/>`_
* urllib3 -- `<https://urllib3.readthedocs.io/>`_
* Python urllib.request -- `<https://docs.python.org/3/library/urllib.request.html>`_

Async:

* HTTPX -- `<https://www.python-httpx.org/>`_
* AIOHTTP -- `<https://docs.aiohttp.org/en/stable/>`_

The recommended HTTP transport library is HTTPX.

::

   $ pip install -U httpx

Select an HTTP library
----------------------

If you have multiple HTTP libraries installed and want to force your RedditWarp
program to use a particular one, add a line like the following to your
program's `__main__` module.

::

   import redditwarp.http.transport.connectors.requests  # noqa: F401

This line forces RedditWarp to use the Requests library as the HTTP transport.
If Requests is not installed, a `ModuleNotFoundError` exception will be thrown
on this line.
