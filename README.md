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
from pycps_sysmlv2 import load_architecture

architecture = load_architecture("tests/fixtures/fixture_a")
system = architecture.part_definitions["FixtureAComposition"]

for connection in system.connections:
    print(connection.src_part_def.name, "->", connection.dst_part_def.name)
```

## Public API

```python
from pycps_sysmlv2 import load_architecture, load_system
from pycps_sysmlv2 import export_architecture, export_architecture_files
```

- `load_architecture(path)`
- `load_system(path, system_part)`
- `export_architecture(architecture, mode="declared" | "flattened")`
- `export_architecture_files(architecture, mode="declared")`

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
