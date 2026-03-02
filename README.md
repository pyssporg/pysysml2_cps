# pycps_sysmlv2

Standalone Python SysML v2 parsing and helper utilities for CPS development.

## What this module does

`pycps_sysmlv2` parses lightweight SysML v2 text files (`*.sysml`) into one connected in-memory architecture model.

It is designed for:
- loading component architectures in scripts/tests
- inspecting parts, ports, attributes, and requirements
- traversing resolved wiring (`connect ... to ...`)
- building validation/reporting tooling on top of parsed model objects

It is not a full SysML v2 compiler. It intentionally targets a practical subset.

## Quickstart

```python
from pycps_sysmlv2 import SysMLParser

architecture = SysMLParser("tests/fixtures/fixture_a").parse()
system = architecture.get_part("FixtureAComposition")

for connection in system.connections:
    print(connection.src_part_def.name, "->", connection.dst_part_def.name)
```

## Public API

```python
from pycps_sysmlv2 import SysMLParser
```

- `SysMLParser(path).parse()`
- `architecture.get_part(system_part)`
- `architecture.add_part(...)`, `remove_part(...)`, `add_port(...)`, `remove_port(...)`, `add_requirement(...)`, `remove_requirement(...)`
- `part_def.add_part(...)`, `add_port(...)`, `add_requirement(...)`, `add_connection(...)` and corresponding `remove_*`
- `architecture.export_flattened()`
- `architecture.export_declared()`

## Documentation

- [Getting Started](docs/getting_started.md)
- [SysML Subset Reference](docs/syntax_reference.md)
- [API and Data Model](docs/api_and_model.md)
- [Error Handling](docs/error_handling.md)
- [Architecture Overview](docs/architecture_overview.md)
- [Repository Layout](docs/layout.md)

## Development

Run tests:

```bash
PYTHONPATH=src pytest -q
```
