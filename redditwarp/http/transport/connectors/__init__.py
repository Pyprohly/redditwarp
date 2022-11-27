"""HTTP transport connectors.

Each of the modules in this subpackage represents an HTTP library. Transport connectors
are HTTP libraries that can be used as drivers to make HTTP requests with this library.

When you import a module from this subpackage, the transport library is loaded and
registered as an available transport connector. You can explicitly import a transport
connector module in your program's `__main__` module to have RedditWarp prioritise that
transport connector. If you do this and the transport package is not installed, an
`ImportError` will occur.

Each transport connector module defines a connector class and a `new_connector` function
to construct a connector object from zero arguments. The transport's name is in `name`
and its version string is available in `version`.
"""
