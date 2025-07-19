#!/usr/bin/env python3
"""
Unit tests for the client module.
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock, PropertyMock  # Import PropertyMock
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
    import requests
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
            "login": org_name,
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}

        # Instantiate the client
        client = GithubOrgClient(org_name)

        # Call the org property (not method)
        result = client.org  # Corrected: Removed parentheses

        # Assert that get_json was called exactly once with the expected URL
        mock_get_json.assert_called_once_with(expected_url)

        # Optionally, assert the return value of org()
        self.assertEqual(result, {
                         "login": org_name,
                         "repos_url":
                         f"https://api.github.com/orgs/{org_name}/repos"})

    def test_public_repos_url(self) -> None:
        """
        Tests that GithubOrgClient._public_repos_url returns the expected URL
        based on a mocked org property.
        """
        # Define a known payload that the mocked org property will return
        test_payload = {"repos_url": "http://mocked-repos-url.com"}

        # Use patch as a context manager to mock GithubOrgClient.org
        # patch.object is used because 'org' is a property on the instance.
        with patch.object(
                GithubOrgClient, 'org', new_callable=Mock) as mock_org:
            # Configure the mocked 'org' property to return our test_payload
            mock_org.return_value = test_payload

            # Instantiate the client
            client = GithubOrgClient("test_org")

            # Access the _public_repos_url property
            result = client._public_repos_url

            # Assert that the mocked 'org' property
            # was accessed (called) exactly once
            mock_org.assert_called_once()

            # Assert that the result of _public_repos_url is the expected one
            self.assertEqual(result, test_payload["repos_url"])

    @patch('test_client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Tests that GithubOrgClient.public_repos returns the expected
        list of repos and that mocked methods/properties are called once.
        """
        # Define the payload that get_json will return
        # when called by repos_payload
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "gpl-3.0"}},
        ]
        mock_get_json.return_value = test_repos_payload

        # Define the URL that _public_repos_url property will return
        test_public_repos_url = "http://mocked-repos-url.com/repos"

        # Patch GithubOrgClient._public_repos_url as a context manager
        # Use new_callable=PropertyMock because _public_repos_url is a property
        with patch.object(
                GithubOrgClient, '_public_repos_url',
                new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = test_public_repos_url

            # Instantiate the client
            client = GithubOrgClient("test_org")

            # Call public_repos
            result = client.public_repos()

            # Assertions
            # 1. Test that the list of repos is what you expect
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)

            # 2. Test that the mocked property
            # (_public_repos_url) was accessed once
            mock_public_repos_url.assert_called_once()

            # 3. Test that the mocked get_json was called once
            # It should be called with the URL returned by _public_repos_url
            mock_get_json.assert_called_once_with(test_public_repos_url)


if __name__ == '__main__':
    unittest.main()
