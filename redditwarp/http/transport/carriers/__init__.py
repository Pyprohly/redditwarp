"""HTTP transport carriers.

This subpackage's modules each represent an HTTP library. HTTP transport carriers
are the various HTTP libraries that can be used as a driver to make HTTP requests
with this library.

When you import a module from this subpackage, the HTTP transport library is loaded
and registered as an accessible HTTP transport. You can explicitly import a carrier
module in your program's `__main__` module to have RedditWarp prioritise that carrier.
If you do this and the carrier package is not installed, an ImportError will occur.

Each carrier module defines a `Session` class and a `new_session` function to construct
a session object from zero arguments. The transport's name is in `name` and its version
string is available in `version`.
"""
