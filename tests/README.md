# Test Fixtures

Public API tests now use small, focused inline SysML models split across:

- `tests/test_public_api_file_loader.py`
- `tests/test_public_api_parts.py`
- `tests/test_public_api_ports.py`
- `tests/test_public_api_requirements.py`
- `tests/test_public_api_inheritance.py`

This folder keeps checked-in JSON architecture snapshots written by those tests:

- `public_api_references/`: parser output snapshots for quick debugging and git diffing
