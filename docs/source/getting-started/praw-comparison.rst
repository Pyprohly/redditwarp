
:orphan:

===============
PRAW Comparison
===============

PRAW
----

PRAW (**P**\ ython **R**\ eddit **A**\ PI **W**\ rapper)
is the original Python package providing a simple interface for interacting
with the Reddit API. Since its initial release way back in 2010, PRAW has been
actively developed and maintained by multiple contributors, and thus has good
support for many of the Reddit API's features.

PRAW repository: `<https://github.com/praw-dev/praw>`_.

RedditWarp
----------

RedditWarp was created as a successor to the prevalent PRAW. While PRAW is an
excellent tool for Reddit API interaction, RedditWarp aspires to be the
next-generation API wrapper library, adhering to modern programming norms such
as static typing and featuring a more functional programming style.

RedditWarp was written with static typing principals in mind, and it drives
much of the design of the library. Attributes on model objects are wired up
manually and include complete type annotations. Model types provided are based
on the object being modelled by the exact API data. For instance, it will not
try to shoehorn incomplete user data from a submission object into a single
'`User`' model. In comparison, with PRAW it is even possible to get into
situations where an attribute does not exist on a model object in some cases.

The following list highlights the differences between RedditWarp and PRAW at a
glance.

The API methods are found on the client instead of on object instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of the most notable changes is that RedditWarp's API methods are found
on the client object instead of on model instances.

::

   # PRAW
   reddit.submission('5e1az9').reply("Super rad!")
   # RedditWarp
   client.p.submission.reply('5e1az9', "Very cool!")

One advantage of this is that you don't have to construct object instances if
you just want to explore the available methods.

Some API methods can also be found on models, but these are just shorthands
for the client's methods and are not preferred over directly invoking them::

   subm = client.p.submission.fetch('5e1az9')
   subm.reply("Very cool!")
   # Or
   client.p.submission.reply('5e1az9', "Very cool!")

Fully type complete
~~~~~~~~~~~~~~~~~~~

RedditWarp is a type-complete library. This means that a type checker does not
have to resort to type inference to determine the type of any public symbol.

For normal non-library code it is not suggested that it needs to be type
complete but rather fully typed, which means that the type of any symbol can
be inferred. This is mostly accomplished by adding type annotations to all
function signatures.

Type annotating your code helps you write type-safe code which can eliminate
a whole class of programming errors, helping speed up development. Type-safe
code is easier to maintain and refactor.

No lazy loading
~~~~~~~~~~~~~~~

PRAW 'lazy loads' model objects. This means that the complete data for an
object is not fetched until you first try to access an unavailable attribute
on it.

PRAW::

   >>> subreddit = reddit.subreddit('POWERshell')
   >>> subreddit.display_name
   'POWERshell'
   >>> subreddit.name  # Web request performed here
   't5_2qo1o'
   >>> subreddit.display_name
   'PowerShell'

Model objects in RedditWarp always have complete data, and the data they
contain is never mutated.

Statically provided attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PRAW dynamically provides the attributes on model objects directly from API
data. This means the attribute names always match those of the API's, which
actually may not be convenient in all cases.

RedditWarp::

   >>> subr = client.p.subreddit.fetch_by_name('POWERshell')
   >>> subr.name
   'PowerShell'
   >>> subr.display_name
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   AttributeError: 'Subreddit' object has no attribute 'display_name'
   >>> subr.b.name
   't5_2qo1o'
   >>> subr.b.display_name
   'PowerShell'

In RedditWarp, the attributes are deliberately wired up. This means some
attributes may have a different name to the equivalent PRAW attribute.

The raw attributes can still be accessed through the `.d` or `.b` mappings.
The `.d` attribute holds a raw dictionary object, whereas `.b` is like
`.d` but you can use the the dot selector to access the mapping entries.

Expressive rather than concise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PRAW methods often feature shorthands that perform additional processing or
send multiple requests to ensure a result. In contrast, RedditWarp avoids
providing shorthands as an alternative to composing multiple procedure calls.
(Although it is not an absolute design constraint that one procedure call
must perform one request.)

RedditWarp code tends to be more verbose although more expressive. To
illustrate, the following are examples of PRAW's shortcuts and how they'd
have to be written in RedditWarp.

- Extracting the ID36 from a submission URL and using it to fetch a
  submission object.

PRAW::

   submission = reddit.submission(url="https://www.reddit.com/comments/10ihdqx")

RedditWarp::

   from redditwarp.util.extract_id_from_url import extract_submission_idn_from_url

   subm_id = extract_submission_idn_from_url("https://www.reddit.com/comments/10ihdqx")
   subm = client.p.submission.fetch(subm_id)

- Fetching a user by ID.

One request must be made to convert the fullname ID to a user name,
and then another to fetch the user's data.

PRAW::

   redditor = reddit.redditor(fullname='t2_4x25quk')
   print(redditor.total_karma)

RedditWarp::

   user_summary = client.p.user.get_user_summary('4x25quk')
   if user_summary is None:
       raise Exception
   user = client.p.user.fetch_by_name(user_summary.name)
   print(user.total_karma)

- Modifying a flair emoji's permission settings.

One request must be made to fetch the subreddit's emoji data,
and then one request to fetch the user's data.

PRAW::

   reddit.subreddit("RedditWarp").emoji["chomp"].update(mod_flair_only=True)

RedditWarp::

   emojis = client.p.flair_emoji.retrieve('RedditWarp')
   emoji = emojis['chomp']
   client.p.flair_emoji.set_permissions(
           'RedditWarp',
           emoji.name,
           mod_only=True,
           post_enabled=emoji.post_enabled,
           user_enabled=emoji.user_enabled)

A programming tool, not a moderation tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is nothing special about moderatorship status when it comes to how
things are arranged in the library. For example there are no `.mod`
namespaces like you often find on PRAW objects to access moderator actions.

PRAW::

   submission.mod.lock()

RedditWarp::

   submission.lock()
   # Or
   client.p.submission.lock(submission.idn)

No configuration file format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RedditWarp does not prescribe an equivalent configuration file format like
PRAW's `praw.ini` files, although, `praw.ini` files are supported for your
convenience. To read credentials from a `praw.ini` file use the
:meth:`Client.from_praw_config() <redditwarp.client_SYNC.Client.from_praw_config>`
alternative constructor.

Fetching a submission does not fetch its comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RedditWarp won't fetch submission comment data if you don't ask for it.

Fetching a submission and fetching a submission with comments are different methods.

RedditWarp::

   subm1 = client.p.submission.fetch('10hoczb')

   tree_node = client.p.comment_tree.fetch('10hoczb')
   subm2 = tree_node.value

   assert subm1.idn == subm2.idn

Comment tree traversals must be done manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RedditWarp encourages you to create your own utilities to handle comment trees.
In particular, there is no built-in function to obtain a flattened comment tree list like PRAW's `CommentForest.list()` method. Instead you must write a traversal algorithm yourself, even for this simple use case. The reason being is that all the different intricate traversal requirements of a traversal algorithm cannot easily be expressed by the parameters of a single function.

See :doc:`../user-guide/comment-trees`.
