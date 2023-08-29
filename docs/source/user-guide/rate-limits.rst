
===========
Rate Limits
===========

Rate limits of the Reddit API
-----------------------------

The global rate limit
~~~~~~~~~~~~~~~~~~~~~

The Reddit API employs a global rate limit on a per client ID basis.

The global rate limit is 996 requests per 600 second window (996/600s),
or for application-only grant types it's 600/600s.

The API rate limit headers
^^^^^^^^^^^^^^^^^^^^^^^^^^

When making requests to the Reddit API, `x-ratelimit-*` headers will typically
be returned, which indicate the current values for the global rate limit.

.. csv-table:: Global rate limit headers
   :header: "Header Name", "Description"

   "`x-ratelimit-remaining`","Number of requests remaining in the current window."
   "`x-ratelimit-reset`","Seconds until you enter a new rate limit window and the header values reset."
   "`x-ratelimit-used`","Number of requests you've made in the current rate limit window."

::

   >>> client.p.ping()
   >>> {k: v for k, v in client.http.last.response.headers.items() if 'ratelimit' in k.lower()}
   {'x-ratelimit-remaining': '596.0', 'x-ratelimit-used': '4', 'x-ratelimit-reset': '139'}

When you exceed the rate limit, the `x-ratelimit-remaining` value will stay at `0`
and the `x-ratelimit-used` value will continue to increase::

   {'x-ratelimit-remaining': '2.0', 'x-ratelimit-used': '598', 'x-ratelimit-reset': '299'}
   {'x-ratelimit-remaining': '1.0', 'x-ratelimit-used': '599', 'x-ratelimit-reset': '299'}
   {'x-ratelimit-remaining': '0', 'x-ratelimit-used': '600', 'x-ratelimit-reset': '299'}
   {'x-ratelimit-remaining': '0', 'x-ratelimit-used': '601', 'x-ratelimit-reset': '299'}
   {'x-ratelimit-remaining': '0', 'x-ratelimit-used': '602', 'x-ratelimit-reset': '299'}

Endpoint-local rate limits
~~~~~~~~~~~~~~~~~~~~~~~~~~

Some endpoints have endpoint-local rate limits, particularly those that involve
creating content on Reddit. Tripping these limits will cause a
`case RedditError(label='RATELIMIT')` exception.

Here is an example of dealing with a `RATELIMIT` API error::

   try:
       client.p.comment.reply(1234, 'text')

   except redditwarp.exceptions.RedditError as e:
       if e.label == 'RATELIMIT':
           time.sleep(600)
       else:
           raise

       client.p.comment.reply(1234, 'text')

When can a 429 HTTP error occur?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Other than exceeding the global ratelimit, a 429 can occur when using the
`POST /api/morechildren` endpoint for comment tree traversals and more than
one concurrent call is made to this endpoint. Reddit disallows simultaneous
requests to this endpoint.

Another scenario where a 429 error might arise is if your user agent string
contains the substring `curl` anywhere. Fortunately, there are few English
words that contain this substring.

How rate limiting is handled by RedditWarp
------------------------------------------

The library automatically handles rate limiting and you shouldn't need to
include sleep calls in your program to stay within Reddit's API limits.

Both the sync and async clients use the same rate limiting logic, which is a
token bucket algorithm. It allows the first few requests to be sent
immediately, which is particularly useful for interactive use.

Running multiple scripts under the same account is not advisable as it can
confuse the rate limiting logic. Instead, try to automate a single account
using asynchronous patterns within a single program.
