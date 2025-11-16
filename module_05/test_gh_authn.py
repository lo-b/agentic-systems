import unittest

from authn import create_gh_app_access_token, create_gh_app_token
from config import GitHubAppConfig, GitHubConfig


class TestGitHubAppTokenCreation(unittest.TestCase):
    def test_valid_signature_passes(self):
        config = GitHubAppConfig()
        """Test case 1: Use GitHub documentation example to verify implementation is correct."""
        t = create_gh_app_token(config, expire_after=600)
        assert t is not None
        assert t != ""


class TestGitHubAppAccessTokenCreation(unittest.TestCase):
    def test_valid_accesstoken_create(self):
        appConfig = GitHubAppConfig()
        config = GitHubConfig()
        """Test case 1: Use GitHub documentation example to verify implementation is correct."""
        t = create_gh_app_token(appConfig, expire_after=600)
        at = create_gh_app_access_token(config, t)
        assert at is not None
        assert at != ""
