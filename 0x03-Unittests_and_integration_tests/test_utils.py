#!/usr/bin/env python3
"""
unit tests for utils module.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map


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


if __name__ == '__main__':
    unittest.main()
