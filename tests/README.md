# Test Strategy

Tests should be small and standalone.

Each test should keep its input model and expected output readable at a glance, ideally defined directly in the test or in a nearby specialized fixture.

Prefer test-local setup over large shared fixtures so contributors can understand the full scenario without scrolling through long files or jumping to other modules.

Public API tests use small, focused inline SysML models split across:

- `tests/test_public_api_file_loader.py`
- `tests/test_public_api_parts.py`
- `tests/test_public_api_ports.py`
- `tests/test_public_api_requirements.py`
- `tests/test_public_api_inheritance.py`

Public API behavior is primarily asserted using readable structure snapshots directly in tests.
