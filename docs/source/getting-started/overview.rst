
========
Overview
========

RedditWarp is a Reddit API wrapper library written in Python, enabling the
development of robust, statically-typed Reddit bots and programs.

The library can be used to create advanced automations for subreddit moderation
in ways that go beyond the capabilities of AutoModerator_. However, it is
important to note that it is not designed primarily for moderators and they may
find it challenging to use.

.. _AutoModerator: https://mods.reddithelp.com/hc/en-us/articles/360002561632-AutoModerator

Although this library may not be well-suited for beginner programmers,
experienced programmers should find it easy-to-use and familiar. It strives to
be simple to understand and learn by having a consistent programming style
whose design emphasizes consistency, cleanliness, and correctness over brevity.
Additionally, access to well-designed low-level components enables advanced
use-cases. This provides a more powerful and fine-grained tool for working with
the Reddit API than ever before.

The library organizes all the possible API calls it supports on the client
instance as sub-objects of `client.p`::

   >>> import redditwarp.SYNC
   >>> client = redditwarp.SYNC.Client()
   >>> user = client.p.user.fetch_by_name('spez')
   >>> user
   <redditwarp.models.user_SYNC.User object at 0x1034e1000>
   >>> user.id36
   '1w72'
   >>> user.name
   'spez'
   >>> str(user.created_at)
   '2005-06-06 04:00:00+00:00'

The high-level procedure calls return objects called 'models'.
Models represent an API object at a particular point in time.
These objects are never mutated after they are created.

Evidently, RedditWarp code features a functional programming design. The API
calls are organised into a big catalog, and the majority of models objects are
treated as read-only. In terms of your experience, this means that the objects
you work with behave consistently, reducing the cognitive load of learning each
of the different sections of the Reddit API.

Low-level API requests can be made like so::

   >>> d = client.request('GET', '/user/spez/about')['data']
   >>> print(d.keys() == user.d.keys())
   True

The following code is an example of a very small and basic bot script that
monitors `r/test <https://www.reddit.com/r/test>`_ for comments and direct
messages the user `u/test <https://www.reddit.com/user/test>`_ about any
comments containing the string "`Hello World`".

.. literalinclude:: _assets/basic_bot_script.py

If you intend to use this library to create a Reddit bot, please read the
bottiquette_ before wreaking havoc all over the internet.

.. _bottiquette: https://www.reddit.com/wiki/bottiquette

The amount of historical data that can be obtained from Reddit and its API is
limited. For data science or academic research that requires large volumes of
data from Reddit, using the PushShift_ service to bulk download historical
archives is a more suitable option.
Visit `r/pushshift <https://www.reddit.com/r/pushshift>`_ to learn more.

.. _PushShift: https://pushshift.io

If you're familiar with PRAW, take a look at :doc:`this document <praw-comparison>`
that contains extra examples to help you get the hang of RedditWarp quicker.
