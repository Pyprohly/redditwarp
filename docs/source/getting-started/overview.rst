
========
Overview
========

RedditWarp is a Reddit API wrapper library written in Python that can help you
develop robust statically-typed Reddit bots and programs.

The library can be used to create advanced automations for subreddit moderation
in ways that go beyond the capabilities of AutoModerator_. However, it's worth
noting that this tooling is primarily designed for developers and comparatively
may not be as user-friendly for non-technical users.

.. _AutoModerator: https://mods.reddithelp.com/hc/en-us/articles/360002561632-AutoModerator

While this library may not be tailored for beginners, experienced programmers
will likely find it familiar and straightforward. Its consistent programming
style prioritizes cleanliness and correctness over brevity. Moreover, the
inclusion of well-designed low-level components allows for advanced use-cases,
making it a powerful, fine-grained tool for working with the Reddit API.

RedditWarp code features a functional programming design. The API calls are
organized into a comprehensive catalog, and most model objects are treated as
read-only. From a user's perspective, this consistency simplifies working with
different sections of the Reddit API, reducing the cognitive load.

All the possible API calls the library supports are neatly categorized into
sub-objects on the client instance::

   >>> import redditwarp.SYNC
   >>> client = redditwarp.SYNC.Client()
   >>> user = client.p.user.fetch_by_name('Pyprohly')
   >>> user.id36
   '4x25quk'
   >>> user.name
   'Pyprohly'
   >>> str(user.created_at)
   '2017-06-23 15:25:50+00:00'

The high-level procedure calls return objects called 'models'.
Models represent an API resource at a particular point in time.
These objects are never mutated after they are created.

Low-level API requests can also be made::

   >>> d = client.request('GET', '/user/Pyprohly/about')['data']
   >>> print(d.keys() == user.d.keys())
   True

The following code is an example of a basic bot script that
monitors `r/test <https://www.reddit.com/r/test>`_ for comments and direct
messages the user `u/test <https://www.reddit.com/user/test>`_ about any
comments containing the string "`Hello World`".

.. literalinclude:: _assets/basic_bot_script.py

Before using this library to access the Reddit API, please see the
`Reddit Data API Wiki`_ for rules, terms, and conditions.

.. _Reddit Data API Wiki: https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki

If you intend to use this library to create a Reddit bot, please read the
bottiquette_ before wreaking havoc all over the internet.

.. _bottiquette: https://www.reddit.com/wiki/bottiquette

Doing data science?
Know that the amount of historical data that can be obtained from the Reddit
API is limited. For data science or academic research purposes that requires
large volumes of data, using the Pushshift_ service to bulk download historical
archives may be a more suitable option.
Visit `r/pushshift <https://www.reddit.com/r/pushshift>`_ to learn more.

.. _Pushshift: https://pushshift.io

Coming from PRAW? Take a look at :doc:`this document <praw-comparison>` which
contains code examples to help you quickly get up to speed with RedditWarp.
