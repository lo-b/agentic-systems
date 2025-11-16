import hashlib
import hmac


def verify_signature(
    payload_body: bytes, secret_token: str, signature_header: str
) -> bool:
    hash_object = hmac.new(
        secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)
