
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
`obtain_upload_lease()` and `deposit_file()` are commonly found in the
procedure index.

In the following example, we are uploading a flair emoji image.

::

   with open("/Users/danpro/Desktop/Ph03nyx-Super-Mario-Chain-Chomp.png", 'rb') as fh:
       filename = op.basename(fh.name)
       lease = client.p.flair_emoji.create.obtain_upload_lease(sr=SR, filepath=filename)
       client.p.flair_emoji.create.deposit_file(fh, lease)

   client.p.flair_emoji.create.add(SR, 'chomp', lease.s3_object_key)

.. note::
   The endpoint for obtaining an upload lease wants you to declare a file path,
   but you should just give it a filename. Even the Reddit site only provides a
   filename.

There will often also be an `upload()` method as a short hand for the
`obtain_upload_lease()` and `deposit_file()` steps.

This is equivalent to the previous snippet::

   with open("/Users/danpro/Desktop/Ph03nyx-Super-Mario-Chain-Chomp.png", 'rb') as fh:
       lease = client.p.flair_emoji.create.upload(fh, sr=SR)

   client.p.flair_emoji.create.add(SR, 'chomp', lease.s3_object_key)

.. note::
   If you pass a file object that does not come from the Python `open()`
   function then you must explicitly specify the `filepath` parameter to
   `upload()` or you will receive a `ValueError` error. This is because regular
   file objects don't have a `.name` attribute.

In the specific case of flair emojis, the `client.p.flair_emoji.create` object
works as a method to further simplify the process described above as a single
step.

::

   with open("/Users/danpro/Desktop/Ph03nyx-Super-Mario-Chain-Chomp.png", 'rb') as fh:
       client.p.flair_emoji.create(SR, 'chomp', fh)

Inline media for submissions
----------------------------

Although the markdown submission format does not support inline media directly,
markdown can be written with image directives and then converted to rich text
JSON for use in the
:meth:`client.p.submission.create_text_post() <redditwarp.siteprocs.submission.SYNC.SubmissionProcedures.create_text_post>`
method.

::

   with open("/Users/danpro/Desktop/wildflowers.jpg", 'rb') as fh:
       lease = client.p.submission.media_uploading.upload(fh)

   text = f'''\
   Look at these nice flowers.

   ![img]({lease.media_id} "Wildflowers")
   '''
   rtj = client.p.misc.convert_markdown_to_richtext(text)
   client.p.submission.create_text_post(SR, 'Nice flowers', rtj)

Uploading videos for video posts
--------------------------------

The endpoint for creating video submissions requires a video and an image as a thumbnail.

Note that the web UI doesn't require you to upload a thumbnail image separately.
Don't ask how the web UI extracts an image from your video; I haven't figured this out yet.

::

   with open("/Users/danpro/Desktop/video.mp4", 'rb') as fh:
       video_lease = client.p.submission.media_uploading.upload(fh)

   with open("/Users/danpro/Desktop/image.jpg", 'rb') as fh:
       image_lease = client.p.submission.media_uploading.upload(fh)

   video_location = video_lease.location
   image_location = image_lease.location
   print(video_location)
   print(image_location)

   client.p.submission.create_video_post(
           'Pyprohly_test3',
           'My great video',
           video_location,
           image_location)
