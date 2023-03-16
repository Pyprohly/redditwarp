
==========
Pagination
==========

Paginators assist the retrieval of large result sets one page at a time.

In the procedure index you'll find many methods with the term `pull` in their
name. These methods return objects that rely on pagination via a
:class:`~redditwarp.pagination.paginator.Paginator` object.

::

   client.p.front.pull.hot()
   client.p.subreddit.pull_new_comments()
   client.p.message.pulls.inbox()

::

   >>> it = client.p.front.pull.hot(amount=5)
   >>> l = list(it)
   >>> for subm in l:
   ...     print("r/{0.subreddit.name} | {0.id36}+ ^{0.score} | {0.title!r:.80}".format(subm))
   ...
   r/todayilearned | 10det5c+ ^13346 | 'TIL Hirsoshima, Japan is one of the few places outside of the US that celebrate
   r/worldnews | 10dc1oj+ ^33566 | 'CIA director secretly met with Zelenskyy before invasion to reveal Russian plot
   r/pics | 10dd7oi+ ^11680 | 'Brendan Fraser with his Critics Choice Award for The Best Actor'
   r/oddlysatisfying | 10dbc7f+ ^27042 | 'Carrots stacked on a truck'
   r/UpliftingNews | 10dc0iu+ ^7746 | 'The price of solar panels is set to plunge'

The pull methods don't return a `Paginator` object directly but instead they
are wrapped in a convenience iterator,
:class:`~redditwarp.pagination.paginator_chaining_iterator.PaginatorChainingIterator`,
which chains the results of each page together when iterated over.

The `amount` parameter on the pull methods can be used to limit the number of
results that get returned from the iterator. A setting of `amount=None` (which
is often the default) means to retrieve as many items as possible from the
source. Be careful when using something like `list()` on these iterators with
`amount=None` because some paginators can go on indefinitely, such as the front
page listings.

Depending on the nature of your application, it may be more convenient to use
the actual `Paginator` object directly. For the time being, the paginator can
be accessed expediently through the
:meth:`~redditwarp.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator.get_paginator`
method on an
'`ImpartedPaginatorChainingIterator`' instance.

Using a `Paginator`, if we want to retrieve 3 pages of up to 5 results each, we
could do so like this::

   import redditwarp.SYNC
   client = redditwarp.SYNC.Client()

   it = client.p.front.pull.hot()
   paginator = it.get_paginator()
   paginator.limit = 5
   for _ in range(3):
       page = paginator.fetch()
       if not page:
           break

       for subm in page:
           print("r/{0.subreddit.name} | {0.id36}+ ^{0.score} | {0.title!r:.80}".format(subm))
       print('---')

Nevertheless, using `.fetch()` and checking if the result is empty is not the
best technique for traversing a paginator in general, because the underlying
pagination structure may have a mechanism to indicate that the next fetch will
return no items, and if this is the case then our algorithm above will
make an additional network request that will be redundant.

If the paginator implements :class:`~redditwarp.pagination.paginator.HasMore`,
we could use the `.has_more()` method to
check if there are more results to consume and break the loop before calling
`.fetch()` again, but it's best to just disregard this and take advantage
of the fact that paginators are iterable and use paginator iterators.

Paginator iterators will consume all items from the source until there are no
more, taking into account whether the underlying pagination structure indicates
that there are no more items available.

When working with paginator iterators, we use `next(pitr, None)` instead of
`paginator.fetch()`.

::

   pitr = iter(paginator)
   for _ in range(3):
       page = next(pitr, None)
       if page is None:
           break

       for subm in page:
           print("r/{0.subreddit.name} | {0.id36}+ ^{0.score} | {0.title!r:.80}".format(subm))
       print('---')

A possibly cleaner alternative:

::

   from itertools import islice

   for page in islice(paginator, 3):
       for subm in page:
           print("r/{0.subreddit.name} | {0.id36}+ ^{0.score} | {0.title!r:.80}".format(subm))
       print('---')

Note, if an exception occurs inside a `Paginator` iterator, the iterator breaks
and a new one must be created.
