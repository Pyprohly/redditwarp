'''
def test_structure(user_client):
	client = user_client
	submissions = client.fetch.submissions
	assert callable(submissions)
	assert callable(submissions.by_id36)
	assert callable(submissions.via_call_chunks)
	assert callable(submissions.via_call_chunks.by_id36)
	assert callable(submissions.as_textposts)
	assert callable(submissions.as_textposts.by_id36)
	assert callable(submissions.as_textposts.via_call_chunks)
	assert callable(submissions.as_textposts.via_call_chunks.by_id36)
	assert callable(submissions.as_linkposts)
	assert callable(submissions.as_linkposts.by_id36)
	assert callable(submissions.as_linkposts.via_call_chunks)
	assert callable(submissions.as_linkposts.via_call_chunks.by_id36)
'''
