
=============
Media Uploads
=============

The upload protocol
-------------------

The Reddit API lets you to upload image files in places such as in image posts,
flair emojis, and subreddit banners. The protocol for uploading media files is
fairly consistent.

Uploading is done in two steps: obtaining an upload lease and then depositing
the image to an Amazon S3 bucket using the lease. Methods named
'`obtain_upload_lease()`' and '`deposit_file()`' are commonly found in the
procedure index.

In the following example, we are uploading a flair emoji image.

::

   with open("/Users/danpro/Desktop/Ph03nyx-Super-Mario-Chain-Chomp.png", 'rb') as fh:
       filename = op.basename(fh.name)
       lease = client.p.flair_emoji.create.obtain_upload_lease(sr=SR, filepath=filename)
       client.p.flair_emoji.create.deposit_file(fh, lease)

   client.p.flair_emoji.create.add(SR, 'chomp', lease.s3_object_key)

.. note::
   Supposedly, the endpoint for obtaining an upload lease wants you to declare
   a file path via a parameter named 'filepath', but you should just give it a
   filename. Even the Reddit website only gives a filename during the upload.

There is also an `upload()` method as a shorthand for
`obtain_upload_lease()` and `deposit_file()`.

The following is equivalent to the previous snippet::

   with open("/Users/danpro/Desktop/Ph03nyx-Super-Mario-Chain-Chomp.png", 'rb') as fh:
       lease = client.p.flair_emoji.create.upload(fh, sr=SR)

   client.p.flair_emoji.create.add(SR, 'chomp', lease.s3_object_key)

.. note::
   If you pass a file object that does not come from the Python `open()`
   function then you must explicitly specify the `filepath` parameter to
   `upload()` or you will receive a `ValueError` error. This is because regular
   file objects don't have a `.name` attribute containing the file name.

Specificly for flair emojis, the `client.p.flair_emoji.create` function works
as a way to further simplify the process described above as a single step.

::

   with open("/Users/danpro/Desktop/Ph03nyx-Super-Mario-Chain-Chomp.png", 'rb') as fh:
       client.p.flair_emoji.create(SR, 'chomp', fh)

Inline media for submissions
----------------------------

Although the markdown submission format does not support inline media directly,
markdown can be written with image directives and then converted to rich text
JSON for use in the
:meth:`client.p.submission.create.text() <redditwarp.siteprocs.submission.create.SYNC.Create.text>`
method.

::

   with open("/Users/danpro/Desktop/wildflowers.jpg", 'rb') as fh:
       lease = client.p.submission.media_uploading.upload(fh)

   txt = f'''\
   Look at these nice flowers.

   ![img]({lease.media_id} "Wildflowers")
   '''
   rtj = client.p.misc.convert_markdown_to_richtext(txt)
   client.p.submission.create.text(SR, 'Nice flowers', rtj)

Uploading videos for video posts
--------------------------------

The endpoint for creating video submissions requires a video and an image file.
The image is used as thumbnail.

Note that the web UI doesn't require the image file. Unfortunately though, the
process they use for extracting the thumbnail image is unknown, so you'll have
to prepare a thumbnail by yourself separately.

::

   with open("/Users/danpro/Desktop/video.mp4", 'rb') as fh:
       video_lease = client.p.submission.media_uploading.upload(fh)
   with open("/Users/danpro/Desktop/image.jpg", 'rb') as fh:
       image_lease = client.p.submission.media_uploading.upload(fh)

   client.p.submission.create.video(
           'Pyprohly_test3',
           'My great video',
           video_lease.location,
           image_lease.location)
