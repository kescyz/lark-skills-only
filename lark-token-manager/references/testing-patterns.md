# Testing Patterns for Lark API Skills

E2E test structure, token acquisition, and rate limit handling.

## E2E Test Structure

Every test follows: **Create -> Verify -> Cleanup**

```python
#!/usr/bin/env python3
"""E2E tests for lark-{domain} skill."""

import os
import sys
import json
import subprocess
import time

# --- Setup ---
PASSED = 0
FAILED = 0
CLEANUP = []  # Track resources for cleanup

def assert_eq(label, actual, expected):
    global PASSED, FAILED
    if actual == expected:
        PASSED += 1
        print(f"  PASS: {label}")
    else:
        FAILED += 1
        print(f"  FAIL: {label} - expected {expected}, got {actual}")

def assert_true(label, condition):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS: {label}")
    else:
        FAILED += 1
        print(f"  FAIL: {label}")

# --- Token Acquisition ---
def get_token_via_mcp():
    """Get Lark token from MCP server."""
    # In real tests, call MCP server
    # For CI, use LARK_ACCESS_TOKEN env var
    token = os.environ.get("LARK_ACCESS_TOKEN")
    if not token:
        print("SKIP: No LARK_ACCESS_TOKEN set")
        sys.exit(0)
    return token

def get_user_info_via_mcp():
    """Get user info from MCP whoami."""
    # In real tests, call MCP whoami
    # For CI, use env vars
    return {
        "open_id": os.environ.get("LARK_OPEN_ID", ""),
        "user_id": os.environ.get("LARK_USER_ID", ""),
    }

# --- Test Cases ---
def test_create_and_get():
    """Test: Create resource, verify, cleanup."""
    print("\n--- test_create_and_get ---")

    # Create
    result = client.create_{resource}({"name": f"Test {int(time.time())}"})
    resource_id = result.get("guid") or result.get("id")
    assert_true("create returns ID", bool(resource_id))
    CLEANUP.append(resource_id)

    # Verify
    fetched = client.get_{resource}(resource_id)
    assert_true("get returns data", bool(fetched))
    assert_true("name matches", "Test" in fetched.get("name", ""))

def test_list():
    """Test: List resources returns array."""
    print("\n--- test_list ---")
    items = client.list_{resources}()
    assert_true("list returns list", isinstance(items, list))
    assert_true("list not empty", len(items) > 0)

def test_update():
    """Test: Update resource, verify change."""
    print("\n--- test_update ---")

    # Create
    result = client.create_{resource}({"name": f"Update Test {int(time.time())}"})
    resource_id = result.get("guid") or result.get("id")
    CLEANUP.append(resource_id)

    # Update
    client.update_{resource}(resource_id, {"name": "Updated Name"})

    # Verify
    fetched = client.get_{resource}(resource_id)
    assert_eq("name updated", fetched.get("name"), "Updated Name")

def test_delete():
    """Test: Delete resource, verify gone."""
    print("\n--- test_delete ---")

    result = client.create_{resource}({"name": f"Delete Test {int(time.time())}"})
    resource_id = result.get("guid") or result.get("id")

    client.delete_{resource}(resource_id)
    # Verify: get should raise or return empty
    try:
        client.get_{resource}(resource_id)
        assert_true("delete confirmed", False)  # Should have raised
    except Exception:
        assert_true("delete confirmed", True)

# --- Cleanup ---
def cleanup():
    """Delete all test resources."""
    print("\n--- Cleanup ---")
    for resource_id in CLEANUP:
        try:
            client.delete_{resource}(resource_id)
            print(f"  Cleaned: {resource_id}")
        except Exception as e:
            print(f"  Cleanup failed: {resource_id} - {e}")

# --- Main ---
if __name__ == "__main__":
    token = get_token_via_mcp()
    user = get_user_info_via_mcp()

    sys.path.insert(0, os.path.dirname(__file__))
    from lark_api import Lark{Domain}Client

    client = Lark{Domain}Client(
        access_token=token,
        user_open_id=user["open_id"],
        user_id=user.get("user_id")
    )

    try:
        test_create_and_get()
        test_list()
        test_update()
        test_delete()
    finally:
        cleanup()

    print(f"\n{'='*40}")
    print(f"Results: {PASSED} passed, {FAILED} failed")
    print(f"{'='*40}")
    sys.exit(1 if FAILED > 0 else 0)
```

## Test Naming Convention

```
tests/
└── test_e2e_{domain}.py    # Main E2E test file
```

Name test functions: `test_{operation}` or `test_{workflow}`.

## Rate Limit Handling in Tests

Add delays between API-heavy tests:

```python
def test_batch_operations():
    """Test operations that hit rate limits."""
    for i in range(10):
        client.create_{resource}({"name": f"Batch {i}"})
        time.sleep(0.1)  # Space out requests
```

For tests that create many resources, increase cleanup delay:

```python
def cleanup():
    for resource_id in CLEANUP:
        try:
            client.delete_{resource}(resource_id)
        except Exception:
            time.sleep(1)  # Back off on rate limit during cleanup
            try:
                client.delete_{resource}(resource_id)
            except Exception:
                pass
```

## Environment Variables for CI

```bash
# Required
export LARK_ACCESS_TOKEN="u-xxx"      # From MCP get_lark_token
export LARK_OPEN_ID="ou_xxx"          # From MCP whoami

# Optional (domain-specific)
export LARK_USER_ID="xxx"             # For attendee operations
export LARK_CALENDAR_ID="xxx"         # Primary calendar
export LARK_TASKLIST_GUID="xxx"       # Test tasklist
export LARK_BASE_APP_TOKEN="xxx"      # Test base
```

## Validation Checklist

Before submitting a skill, verify:
- [ ] All CRUD operations tested (create, get, list, update, delete)
- [ ] Pagination tested (list returns all items)
- [ ] Error handling tested (invalid input, missing resource)
- [ ] Cleanup runs even if tests fail (use try/finally)
- [ ] No hardcoded tokens or user IDs
- [ ] Test resources use unique names (timestamp-based)
- [ ] Rate limits respected (delays between heavy operations)
