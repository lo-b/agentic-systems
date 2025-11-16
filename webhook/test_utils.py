import unittest

from webhook.utils import verify_signature


class TestVerifySignature(unittest.TestCase):
    SECRET_TOKEN = "It's a Secret to Everybody"
    PAYLOAD_BODY = b"Hello, World!"
    VALID_SIGNATURE_HEADER = (
        "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17"
    )

    def test_valid_signature_passes(self):
        """Test case 1: Use GitHub documentation example to verify implementation is correct."""
        assert verify_signature(
            self.PAYLOAD_BODY, self.SECRET_TOKEN, self.VALID_SIGNATURE_HEADER
        )
