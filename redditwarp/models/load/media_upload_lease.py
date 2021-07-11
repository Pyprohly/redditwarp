
from typing import Mapping, Any

from ..media_upload_lease import MediaUploadLease

def load_media_upload_lease(d: Mapping[str, Any]) -> MediaUploadLease:
    return MediaUploadLease(d)
