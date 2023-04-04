
==========
The Basics
==========

Type safety
-----------

The library is meticulous about static typing and it expects your code to be as
well. It is strongly advised that type annotations are used all throughout your
code to make it fully typed (achieved mostly by adding type annotations to all
function signatures), and then use a type checker to verify type correctness in
your program.

IDEs such as VS Code and PyCharm have built-in type checkers. If you're using a
text editor, popular static type checker tools include
`Mypy <https://github.com/python/mypy>`_ and
`Pyright <https://github.com/microsoft/pyright>`_.

Both are recommended. Mypy's output looks nicer, but Pyright is the strongest
Python type checker.

The default settings for type checkers tend to be too lenient, while their
strict option can be overly strict. The use of the `mypy.ini` (Mypy) and
`pyrightconfig.json` (Pyright) files in the RedditWarp repository provide a
well-balanced middle ground, and it is recommended to use them as a basis for
your own projects if you don't already have a template.

Two IO worlds
-------------

You would have noticed by now the unusual capitalisation of the terms `SYNC`
and `ASYNC` in many of RedditWarp's imports. This is how the library chooses
to support both sync and async IO worlds.

Switching a program's synchronicity is straightforward. To convert a program
into an asynchronous one, all you need to do is change `SYNC` to `ASYNC` in the
imports, add `async` and `await` keywords to the appropriate locations, and
then wrap `main()` in `asyncio.run()`. A type checker will greatly assist you
in this process.

.. tab:: Sync

   .. literalinclude:: _assets/ping_bot_SYNC.py

.. tab:: Async

   .. literalinclude:: _assets/ping_bot_ASYNC.py

To help internalise the convention that's going on here, the `SYNC.py` and
`ASYNC.py` modules can be thought of as everything that would be in the
`__init__.py` file but isn't because it is committed to a particular IO world.
When a module ends with a capital `SYNC`/`ASYNC` it signifies that an analogous
symbol exists in the the opposite module which can be mindlessly switched out
if you decide to switch the synchronicity of your program.

Sometimes, not all IO-committed objects have a perfect counterpart and the name
of the symbol may differ slightly for the sake of correctness, even though they
offer the same functionality. In these cases, the symbols will not be found in
module names ending with `SYNC`/`ASYNC`, but rather in module names ending with
`sync1`/`async1`. It's rare you'll encounter this though.

::

   # SYNC
   from redditwarp.pagination.paginators.subreddit_sync1 import SubredditSearchPaginator
   # ASYNC
   from redditwarp.pagination.paginators.subreddit_async1 import SubredditSearchAsyncPaginator

If it makes sense to use the sync version in an async program, the symbols will
be named without any specific convention. This typically occurs with iterators.

::

   # SYNC
   from redditwarp.iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
   # ASYNC
   from redditwarp.iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator

Model attributes
----------------

The methods of the procedure index return instances of model objects from the
classes within the :mod:`redditwarp.models` subpackage.

The attributes of the models have been deliberately named to be more meaningful
and consistent, and only the most essential ones have been wired up.

The models are never mutated by the library once they are created, and
modifying the attributes on these objects is not recommended.

A model's original data dictionary can be found in a `.d` attribute on the
model.

::

   >>> subm = client.p.submission.fetch(int('10gudzi', 36))
   >>> subm.permalink
   'https://www.reddit.com/r/confusing_perspective/comments/10gudzi/skydiving_fun/'
   >>> subm.d['permalink']
   '/r/confusing_perspective/comments/10gudzi/skydiving_fun/'
   >>> assert subm.permalink_path == subm.d['permalink']
   >>> assert 'permalink_path' not in subm.d
   >>> subm.created_at
   datetime.datetime(2023, 1, 20, 11, 16, 19, tzinfo=datetime.timezone.utc)
   >>> assert 'created_at' not in subm.d
   >>> subm.created_ut
   1674213379
   >>> assert subm.created_ut == subm.d['created_utc']

Oftentimes if there is a `.d` attribute then there will also be a `.b`
attribute which allows access to the items in the `.d` attribute using dot
notation. E.g.::

   assert subm.d['created_utc'] == subm.b.created_utc == subm.b['created_utc']

It is best to avoid using the `.d` and `.b` attribute namespaces as they do not
provide the same level of type-safety as directly accessing attributes on the
object itself does.

Models can also have methods, but they are merely passthroughs to the procedure
index's methods.

::

   subm.delete()
   # <== Functionally identical ==>
   client.p.submission.delete(subm.id)

Models coming from a `SYNC`/`ASYNC` module will often have a non-IO-committed
version with no methods. If you don't intend to use the model methods you can
type your variables as the non-IO version.

E.g.::

   import redditwarp.SYNC
   from redditwarp.models.submission_SYNC import Submission as Submission_IO
   from redditwarp.models.submission import Submission

   client = redditwarp.SYNC.Client()

   subm1: Submission_IO = client.p.submission.fetch(2196778693)
   subm1.delete()  # Valid

   subm2: Submission = subm1
   subm2.delete()  # Invalid  => Mypy :: "Submission" has no attribute "delete"
