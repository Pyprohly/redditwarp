
=============
Comment Trees
=============

Tree node data structures are used to model submission comment trees.

A general tree node is defined as a data class with a `value` and `children`
field. The type of `value` and members of the `children` list are both generic.
Typically though, the `children` field will always be some list of other tree
nodes.

Submission comment tree nodes extend the general tree node data structure and
includes a new field: `more`. This object, if not `None`, is a '`MoreComments`'
callable. Calling it makes a network request and returns another tree node
whose `children` elements should be treated as a continuation of the original
`children` list. The `value` field of this new node will be `None`.

For most nodes in a submission comment tree, the `value` field will be a
`Comment` object, however it will be a `Submission` for the root node, and it
will be `None` for nodes that come from evaluating `MoreComments` callables.

A traversal algorithm is necessary for navigating through a tree structure.
RedditWarp doesn't include any built-in tree traversal methods since there's no
one-size-fits-all approach that covers every need, such as stopping at a
certain depth, limiting the number of `MoreComments` fetches, processing only
leaf node comments, and handling network errors when evaluating `MoreComments`
callables.

A submission's comment tree can be obtained via
:meth:`client.p.comment_tree.fetch() <redditwarp.siteprocs.comment_tree.SYNC.CommentTreeProcedures.fetch>`.

.. tab:: Sync

   .. literalinclude:: _assets/tree_traversals/tree_traversal_demo_SYNC.py

.. tab:: Async

   .. literalinclude:: _assets/tree_traversals/tree_traversal_demo_ASYNC.py

In the preceding code demo, if we ignore the `if root.more:` part it should
look familar as your conventional recursive depth-first search (DFS) traversal
algorithm. If we did remove the `if root.more:` block it would behave as though
only the comments immediately visible on the page are processed without
clicking on any 'load more comments' links.

A DFS traversal of a submission comment tree produces comments in the order in
which they appear when reading the comments from top to bottom on the page.
A BFS, on the other hand, would yield comments in the order of their level,
starting with all top level nodes first, then all second level nodes, then all
third level nodes, and so on.

The recursive DFS algorithm works well, is short, and looks very clean. A big
drawback though is that Python restricts the call stack size to 1000 levels,
making it potentially fragile, even if it's unlikely you'll encounter comment
trees 1000 levels deep. For this reason, an iterative version may be favoured,
however, there are hurdles in creating an iterative version of the algorithm
that looks as tidy.

If you attempt to convert the recursive DFS algorithm into an iterative one,
you may get an inaccurate algorithm where the order in which the `MoreComments`
callables are evaluated is incorrect. In the iterative version, the
`MoreComments` callables are evaluated as soon as the nodes are encountered,
whereas in the recursive version, the `MoreComments` callable of the innermost
nodes are evaluated first, which should be the correct order of evaluation.
In the end, it's technically a non-functional difference, but it does have a
noticeable effect on scripts that display comment trees. Namely, the output of
an incorrect iterative version will appear to be more jittery and slower than
a recursive one.

RedditWarp includes a demonstrational command line tool to visualise Reddit
submission comment trees. Try running these two on the command line. The
`--algo=dfs0` option selects the recursive algorithm and `--algo=dfs1` is the
iterative one. Do you notice any difference in the pace of output?

::

   python -m redditwarp.cli.comment_tree --algo=dfs0 t44sm0

The longer, 'correct', iterative DFS and BFS traversal algorithms are
recommended. These are significantly uglier than the shorter iterative
versions, but they are more accurate to the correct order in which the
`MoreComments` callables should be evaluated.

The traversal algorithm recipes are illustrated below.

Traversal recipes
-----------------

Depth-first, recursive
~~~~~~~~~~~~~~~~~~~~~~

(`dfs0`)

.. tab:: Sync

   .. literalinclude:: _assets/tree_traversals/dfs0_SYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

.. tab:: Async

   .. literalinclude:: _assets/tree_traversals/dfs0_ASYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

A recursive DFS. The algorithm looks clean and performs well, except that
Python limits the maximum function recursion depth to 1000, so if you have a
very deep comment tree you'll have to use an iterative approach.

Depth-first, iterative, inaccurate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(`dfs1`)

.. tab:: Sync

   .. literalinclude:: _assets/tree_traversals/dfs1_SYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

.. tab:: Async

   .. literalinclude:: _assets/tree_traversals/dfs1_ASYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

An iterative DFS that is functionally equivalent to the recursive version but
is slightly inaccurate because the `MoreComments` callables are evaluated
before the child nodes are processed. It's undesirable because for a display
script it has the effect of feeling slower and looking more jittery.

Depth-first, iterative, accurate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(`dfs2`)

.. tab:: Sync

   .. literalinclude:: _assets/tree_traversals/dfs2_SYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

.. tab:: Async

   .. literalinclude:: _assets/tree_traversals/dfs2_ASYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

This version is more algorithmically accurate to the recursive one but at the
cost of looking messier.

Breadth-first, inaccurate
~~~~~~~~~~~~~~~~~~~~~~~~~

(`bfs1`)

.. tab:: Sync

   .. literalinclude:: _assets/tree_traversals/bfs1_SYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

.. tab:: Async

   .. literalinclude:: _assets/tree_traversals/bfs1_ASYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

This BFS traversal evaluates the `MoreComments` callables before processing the
children which, we've established is undesirable because it feels slow.

Breadth-first, accurate
~~~~~~~~~~~~~~~~~~~~~~~

(`bfs2`)

.. tab:: Sync

   .. literalinclude:: _assets/tree_traversals/bfs2_SYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

.. tab:: Async

   .. literalinclude:: _assets/tree_traversals/bfs2_ASYNC.py
      :start-after: #region::literalinclude
      :end-before: #endregion

A BFS that processes all children before evaluating `MoreComments` callables.
Algorithmically better but programmatically *much* uglier.
