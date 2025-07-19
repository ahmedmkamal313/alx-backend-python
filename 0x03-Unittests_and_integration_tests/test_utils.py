#!/usr/bin/env python3
"""
Unit tests for the utils module.
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock  # Import patch and Mock
from utils import access_nested_map, get_json  # Import get_json


class TestAccessNestedMap(unittest.TestCase):
    """
    Tests the access_nested_map function from the utils module.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: dict, path: tuple, expected_result: any) -> None:
        """
        Tests that access_nested_map returns the expected result for various inputs.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected_result)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map: dict, path: tuple, expected_key: str) -> None:
        """
        Tests that access_nested_map raises a KeyError with the expected message
        for invalid paths or non-mapping intermediate values.
        """
        with self.assertRaisesRegex(KeyError, f"'{expected_key}'"):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """
    Tests the get_json function from the utils module.
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get')  # Patch requests.get for this test method
    def test_get_json(self, test_url: str, test_payload: dict, mock_get: Mock) -> None:
        """
        Tests that get_json returns the expected result and
        that requests.get is called exactly once with the correct URL.
        """
        # Configure the mocked requests.get to return a Mock object
        # whose .json() method returns test_payload
        mock_get.return_value.json.return_value = test_payload

        # Call the function under test
        result = get_json(test_url)

        # Assert that the mocked get method was called exactly once with test_url as argument
        mock_get.assert_called_once_with(test_url)

        # Assert that the output of get_json is equal to test_payload
        self.assertEqual(result, test_payload)


if __name__ == '__main__':
    unittest.main()
