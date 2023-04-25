
from dataclasses import dataclass

from .upload_lease import UploadLease

@dataclass(repr=False, eq=False)
class SubmissionMediaUploadLease(UploadLease):
    media_id: str
    declared_filepath: str
    websocket_url: str
