#!/usr/bin/env python3
"""
Unit tests for the client module.
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from typing import (
    List,
    Dict,
    Any,
    Callable,
    Mapping,
    Sequence,
)
import functools  # Added import for functools

# Re-define utils functions here or ensure they are importable
# For the purpose of this self-contained test file, let's include them
# as they are needed by GithubOrgClient.
# In a real project, these would be imported from a 'utils' module.

# Copied from utils.py for self-containment as per common testing patterns
# where dependencies are sometimes inlined or explicitly provided for tests.


def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """Access nested map with key path."""
    for key in path:
        if not isinstance(nested_map, Mapping):
            raise KeyError(key)
        nested_map = nested_map[key]
    return nested_map


def get_json(url: str) -> Dict:
    """Get JSON from remote URL."""
    # In a real scenario, this would make an actual HTTP request.
    # For testing, it will be mocked.
    import requests  # Keep import here to avoid circular dependency if utils imports client
    response = requests.get(url)
    return response.json()


def memoize(fn: Callable) -> Callable:
    """Decorator to memoize a method."""
    attr_name = "_{}".format(fn.__name__)

    @functools.wraps(fn)
    def memoized(self):
        """"memoized wraps"""
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return property(memoized)


class GithubOrgClient:
    """A Github org client
    """
    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        """Init method of GithubOrgClient"""
        self._org_name = org_name

    @memoize
    def org(self) -> Dict:
        """Memoize org"""
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        """Public repos URL"""
        return self.org["repos_url"]

    @memoize
    def repos_payload(self) -> Dict:
        """Memoize repos payload"""
        return get_json(self._public_repos_url)

    def public_repos(self, license: str = None) -> List[str]:
        """Public repos"""
        json_payload = self.repos_payload
        public_repos = [
            repo["name"] for repo in json_payload
            if license is None or self.has_license(repo, license)
        ]
        return public_repos

    @staticmethod
    def has_license(repo: Dict[str, Dict], license_key: str) -> bool:
        """Static: has_license"""
        assert license_key is not None, "license_key cannot be None"
        try:
            has_license = access_nested_map(
                repo, ("license", "key")) == license_key
        except KeyError:
            return False
        return has_license


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests the GithubOrgClient class.
    """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    # Patch the get_json function within this test_client module
    @patch('test_client.get_json')
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """
        Tests that GithubOrgClient.org returns the correct value
        and that get_json is called exactly once with the expected argument.
        """
        # Define the expected URL based on the org_name
        expected_url = GithubOrgClient.ORG_URL.format(org=org_name)

        # Configure the mock_get_json to return a dummy payload
        # The actual content of the payload doesn't matter for this test,
        # as we are only testing if get_json is called correctly.
        mock_get_json.return_value = {
            "login": org_name, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}

        # Instantiate the client
        client = GithubOrgClient(org_name)

        # Call the org property (not method)
        result = client.org  # Corrected: Removed parentheses

        # Assert that get_json was called exactly once with the expected URL
        mock_get_json.assert_called_once_with(expected_url)

        # Optionally, assert the return value of org()
        self.assertEqual(result, {
                         "login": org_name, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"})


if __name__ == '__main__':
    unittest.main()
