# 🧪 0x03 - Unittests and Integration Tests

This directory contains unit and integration tests for a Python client interacting with the GitHub API. The tests are designed to ensure the correctness and robustness of the `GithubOrgClient` class and its associated utility functions.

---

## 📁 Directory Contents

- **`test_client.py`**  
  Contains:
  - Unit tests for methods of `GithubOrgClient` (e.g., `.org`, `._public_repos_url`, `.public_repos`, `.has_license`).
  - Integration tests using mocked external HTTP requests via `unittest.mock` and `parameterized_class`.
  - Imports:
    - `GithubOrgClient` from `client.py`
    - Utility functions from `utils.py`: `get_json`, `access_nested_map`, `memoize`

- **`test_utils.py`**  
  Contains:
  - Unit tests for utility functions in `utils.py`
  - Tests for:
    - `access_nested_map`: including expected results and exception cases
    - `get_json`: uses `patch` to mock `requests.get`
    - `memoize`: ensures a decorated method caches its result after the first call

- **`client.py`**  
  Contains the `GithubOrgClient` class, which interacts with the GitHub API to retrieve organization and repository data.

- **`utils.py`**  
  Provides reusable utility functions used by the client:
  - `get_json()`: makes GET requests and parses JSON
  - `access_nested_map()`: safely accesses nested dictionary paths
  - `memoize`: a decorator for caching method results

- **`fixtures.py`**  
  Provides static fixture data (mock GitHub API payloads) used for deterministic integration tests without making real HTTP requests.

---

## 🧪 Testing Frameworks

- `unittest`: Python's built-in testing framework
- `unittest.mock`: for mocking dependencies (like HTTP requests)
- `parameterized`: allows writing parameterized tests with different inputs
- `parameterized_class`: for integration test grouping

---

## ▶️ How to Run the Tests

From within the `0x03-Unittests_and_integration_tests` directory:

```bash
python3 -m unittest test_client.py
python3 -m unittest test_utils.py
```

These commands will discover and run all defined test cases.

---

## 🎯 Test Objectives

- ✅ Ensure correctness of `GithubOrgClient` methods
- ✅ Validate proper mocking of external dependencies (like `requests.get`)
- ✅ Verify that memoization via `@memoize` is effective
- ✅ Confirm correct parsing and access of nested structures in JSON
- ✅ Ensure utility functions raise meaningful exceptions when needed

---

## 🔐 Highlights

- Fully isolated unit tests with mocking
- Reliable, repeatable integration tests using fixtures
- Coverage includes both API behavior and utility function correctness
- No real HTTP requests are made during testing
