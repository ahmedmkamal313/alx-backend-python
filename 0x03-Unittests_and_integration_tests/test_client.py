#!/usr/bin/env python3
"""
Unit tests for the client module.
"""
import unittest
import functools
from typing import (
    List,
    Dict,
    Any,
    Callable,
    Mapping,
    Sequence,
)
from unittest.mock import patch, Mock, PropertyMock

from parameterized import parameterized, parameterized_class

# Import fixtures from fixtures.py
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos

# IMPORTANT: These imports assume client.py and utils.py exist as separate files
# and contain the respective classes/functions.
from client import GithubOrgClient
from utils import get_json, access_nested_map, memoize


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests the GithubOrgClient class.
    """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('utils.get_json')  # Correctly patch utils.get_json
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """
        Tests that GithubOrgClient.org returns the correct value
        and that get_json is called exactly once with the expected argument.
        """
        # Define the expected URL based on the org_name
        expected_url = GithubOrgClient.ORG_URL.format(org=org_name)

        # Configure the mocked get_json to return a dummy payload
        mock_get_json.return_value = {
            "login": org_name,
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        }

        # Instantiate the client
        client = GithubOrgClient(org_name)

        # Call the org property (not method)
        result = client.org

        # Assert that get_json was called exactly once with the expected URL
        mock_get_json.assert_called_once_with(expected_url)

        # Optionally, assert the return value of org()
        self.assertEqual(result, {
            "login": org_name,
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        })

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

            # Instantiate the client (org_name doesn't matter for this test
            # as 'org' is mocked)
            client = GithubOrgClient("test_org")

            # Access the _public_repos_url property
            result = client._public_repos_url

            # Assert that the mocked 'org' property was accessed (called)
            # exactly once
            mock_org.assert_called_once()

            # Assert that the result of _public_repos_url is the expected one
            self.assertEqual(result, test_payload["repos_url"])

    @patch('utils.get_json')  # Correctly patch utils.get_json
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Tests that GithubOrgClient.public_repos returns the expected list
        of repos and that mocked methods/properties are called once.
        """
        # Define the payload that get_json will return when called by
        # repos_payload
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

            # 2. Test that the mocked property (_public_repos_url) was
            # accessed once
            mock_public_repos_url.assert_called_once()

            # 3. Test that the mocked get_json was called once
            # It should be called with the URL returned by _public_repos_url
            mock_get_json.assert_called_once_with(test_public_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
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
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Performs integration tests for GithubOrgClient.public_repos.
    Mocks external requests using setUpClass and tearDownClass.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Sets up class-level fixtures for integration tests.
        Mocks requests.get to return example payloads from fixtures.
        """
        # Create a patcher for utils.get_json
        # This is the correct target for patching the function
        # that GithubOrgClient uses
        cls.get_patcher = patch('utils.get_json')

        # Start the patcher and store the mock object
        cls.mock_get = cls.get_patcher.start()

        # Define the side_effect for mock_get
        # This function will be called when utils.get_json(url) is invoked.
        def side_effect_func(url):
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                return cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                return cls.repos_payload
            else:
                raise ValueError(f"Unexpected URL in mock: {url}")

        cls.mock_get.side_effect = side_effect_func

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Stops the patcher after all integration tests have run.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Tests the public_repos method of GithubOrgClient in an integration
        context.
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

        # Verify that get_json was called exactly twice in total for this
        # test class:
        # 1. Once for client.org (when its property is accessed)
        # 2. Once for client.repos_payload (when its property is accessed)
        # The memoize decorator ensures these are only called once per instance.
        # We need to check the calls made to the *actual* mock_get
        # (which is utils.get_json).
        calls = [
            unittest.mock.call(GithubOrgClient.ORG_URL.format(org="google")),
            unittest.mock.call(self.org_payload["repos_url"])
        ]
        self.mock_get.assert_has_calls(calls, any_order=True)
        self.assertEqual(self.mock_get.call_count, 2)

    def test_public_repos_with_license(self) -> None:
        """
        Tests the public_repos method with a license filter in an integration
        context.
        Verifies that the method returns the expected list of repository names
        and that get_json is called correctly.
        """
        client = GithubOrgClient("google")

        # Test public_repos with an Apache-2.0 license filter
        repos_apache2 = client.public_repos(license="apache-2.0")
        self.assertEqual(repos_apache2, self.apache2_repos)

        # Ensure get_json was called twice for this instance
        # (due to memoization)
        # The calls should be the same as in test_public_repos without license
        calls = [
            unittest.mock.call(GithubOrgClient.ORG_URL.format(org="google")),
            unittest.mock.call(self.org_payload["repos_url"])
        ]
        self.mock_get.assert_has_calls(calls, any_order=True)
        self.assertEqual(self.mock_get.call_count, 2)


if __name__ == '__main__':
    unittest.main()
