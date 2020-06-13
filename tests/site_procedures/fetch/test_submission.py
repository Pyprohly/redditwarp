'''
def test_structure(user_client):
	client = user_client
	submission = client.fetch.submission
	assert callable(submission)
	assert callable(submission.by_id36)
	assert callable(submission.as_textpost)
	assert callable(submission.as_textpost.by_id36)
	assert callable(submission.as_linkpost)
	assert callable(submission.as_linkpost.by_id36)
'''
