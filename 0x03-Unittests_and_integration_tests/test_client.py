#!/usr/bin/env python3
"""
Unit tests for the client module.
"""
import unittest
from parameterized import parameterized, parameterized_class, TestCase
from unittest.mock import patch, Mock, PropertyMock
from typing import (
    List,
    Dict,
    Any,
    Callable,
    Mapping,
    Sequence,
)
import functools
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos

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

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        # Added test case for missing 'key'
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),  # Added test case for missing 'license'
    ])
    def test_has_license(self, repo: Dict[str, Dict],
                         license_key: str, expected_result: bool) -> None:
        """
        Tests that GithubOrgClient.has_license returns the expected boolean
        value based on the provided repository dictionary and license key.
        """
        self.assertEqual(GithubOrgClient.has_license(
            repo, license_key), expected_result)
@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(TestCase):
    """
    Performs integration tests for GithubOrgClient.public_repos.
    Mocks external requests using setUpClass and tearDownClass.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Sets up class-level fixtures for integration tests.
        Mocks requests.get to return example payloads found in the fixtures.
        """
        # Create a patcher for requests.get
        cls.get_patcher = patch('requests.get')

        # Start the patcher and store the mock object
        cls.mock_get = cls.get_patcher.start()

        # Define the side_effect for mock_get.return_value.json
        # This function will be called when
        # requests.get(url).json() is invoked.
        def side_effect_func(url):
            mock_response = Mock()
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            else:
                # Handle unexpected URLs if necessary, or raise an error
                raise ValueError(f"Unexpected URL in mock: {url}")
            return mock_response

        cls.mock_get.side_effect = side_effect_func

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Stops the patcher after all integration tests have run.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Tests the public_repos method of GithubOrgClient
        in an integration context.
        Verifies that the method returns the expected list of repository names
        and that get_json is called correctly.
        """
        # Instantiate the client with an org name that matches the fixture
        client = GithubOrgClient("google")

        # Test public_repos without a license filter
        repos_no_filter = client.public_repos()
        self.assertEqual(repos_no_filter, self.expected_repos)

        # Test public_repos with an Apache-2.0 license filter
        repos_apache2 = client.public_repos(license="apache-2.0")
        self.assertEqual(repos_apache2, self.apache2_repos)

        # Verify that get_json was called exactly
        # twice in total for this test class:
        # 1. Once for client.org
        # 2. Once for client.repos_payload
        # The memoize decorator ensure these are only called once per instance
        # We need to check the calls made to the *actual* mock_get.
        # Since client.org and client.repos_payload are
        # memoized, get_json is called
        # once for each of them *per instance of GithubOrgClient*.
        # The total calls to mock_get should be 2 for this test method.
        calls = [
            unittest.mock.call(self.org_payload["repos_url"].replace(
                "/repos", "")),  # Call for org()
            # Call for repos_payload()
            unittest.mock.call(self.org_payload["repos_url"])
        ]
        self.mock_get.assert_has_calls(calls, any_order=True)
        self.assertEqual(self.mock_get.call_count, 2)


if __name__ == '__main__':
    unittest.main()
