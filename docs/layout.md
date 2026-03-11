# Repository Layout

The repository is organized as a standard `src/` layout Python package.

## Top-Level Directories

- `src/pycps_sysmlv2/` - package source code
- `tests/` - unit, regression, and public API tests
- `docs/` - user and developer documentation
- `examples/` - runnable documentation examples

## Important Files

- `pyproject.toml` - package metadata and test configuration
- `README.md` - project overview and entry-point documentation
- `LICENSE` - project license

## Source Layout

- `src/pycps_sysmlv2/parser/` - parser orchestration and linking passes
- `src/pycps_sysmlv2/definitions/` - domain model classes
- `src/pycps_sysmlv2/exporter.py` - declared and flattened SysML export
- `src/pycps_sysmlv2/parser_utils.py` - parsing and serialization helpers

## Test Layout

- `tests/test_public_api_*.py` - public API and parsing behavior by concern
- `tests/test_error_handling.py` - failure-mode coverage
- `tests/test_public_api_mutation.py` - model mutation API coverage
- `tests/test_type_utils.py` - type inference and normalization coverage

For test-style conventions, see [tests/README.md](../tests/README.md).
