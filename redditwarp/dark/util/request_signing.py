pass
'''
https://www.reddit.com/r/hacking/comments/zo43jm/good_reddit/

https://github.com/reddit-archive/reddit/blob/master/r2/r2/lib/signing.py
'''

import hmac
import hashlib


MOBILE_ANDROID_HMAC_KEY: str = "8c7abaa5f905f70400c81bf3a1a101e75f7210104b1991f0cd5240aa80c4d99d"
MOBILE_IOS_HMAC_KEY: str = ""  # Unknown

VENDOR_HEADER_NAME: str = 'client-vendor-id'
SIGNATURE_UA_HEADER_NAME: str = 'X-hmac-signed-result'
SIGNATURE_BODY_HEADER_NAME: str = 'X-hmac-signed-body'

SIGNATURE_UA_MESSAGE_TEMPLATE: str = "Epoch:%d|User-Agent:%s|Client-Vendor-ID:%s"
SIGNATURE_BODY_MESSAGE_TEMPLATE: str = "Epoch:%d|Body:%s"

SIGNATURE_TEMPLATE: str = "{global_version}:{platform}:{version}:{epoch}:{hmac_hash}"

VALID_EPOCH_MAX_AGE: float = 5 * 60


def generate_hmac_hash(secret: str, message: str) -> str:
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

def generate_android_mobile_hmac_hash(message: str) -> str:
    return generate_hmac_hash(MOBILE_ANDROID_HMAC_KEY, message)

def get_android_mobile_request_signature(epoch: int, hmac_hash: str) -> str:
    return SIGNATURE_TEMPLATE.format_map({
        'global_version': 1,
        'platform': 'android',
        'version': 2,
        'epoch': epoch,
        'hmac_hash': hmac_hash,
    })
