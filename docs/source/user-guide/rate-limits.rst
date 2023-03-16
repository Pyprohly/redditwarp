
===========
Rate Limits
===========

Rate limits of the Reddit API
-----------------------------

The global rate limit
~~~~~~~~~~~~~~~~~~~~~

The Reddit API employs a global rate limit that is typically applied on a
per user basis. But for application-only grant types, it's per HTTP session.

The global rate limit is 600 requests per a 600 second window (600/600s), which
equates to one request per second. It's 300/600s (1 request every 2 seconds)
for application-only grant types.

.. note::
   Side note, the token server's rate limit is 300 requests over 600 seconds
   (30 times per minute) according to the `x-ratelimit-*` headers.

Interestingly, the global rate limits are not actively enforced by the servers
and you will not receive an immediate error message if you go over the limit.
Theoretically though, exceeding the global rate limit should result in 429 HTTP
errors.

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

It is generally rare to receive a 429 HTTP error, and there are only a few
specific situations where this error may occur.

One such case is when using the `POST /api/morechildren` endpoint for comment
tree traversals, and more than one concurrent call is made to this endpoint.
Reddit disallows multiple simultaneous requests to this endpoint.

Another scenario where a 429 error might arise is if your user agent string
contains the substring `curl` anywhere. Fortunately, there are few English
words that contain this substring.

How rate limiting is handled by the library
-------------------------------------------

You don't need to include sleep calls in your program to stay within the Reddit
API's rate limits, as the library automatically handles rate limiting.

For the sync client, the wait time for each request is calculated by
`x-ratelimit-reset` / `x-ratelimit-remaining`. However, there is additional
logic in place that allows the first few requests to be sent immediately, which
is particularly useful for interactive use.

The async client uses a token bucket rate limiting algorithm with a capacity of
10 and a refresh rate of 1 token per second. Of course, the global rate limit
headers are still monitored though.

You shouldn't have to wait more than 2 seconds for an API call under normal
use.

Running multiple scripts under the same account is not advisable as it can
confuse the rate limiting logic.
