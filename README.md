# pycps_sysmlv2

`pycps_sysmlv2` parses a practical subset of SysML v2 text files into a connected in-memory model for Python tooling.

It is designed for:
- loading one `.sysml` file or a directory of files
- inspecting parts, ports, attributes, requirements, and connections
- resolving references and inheritance during load
- exporting declared or flattened SysML text

It is not a full SysML v2 compiler.

## Install

```bash
pip install -e .
```

## Quick Example

Runnable example:
- `python examples/readme_quick_example.py`
- source: [`examples/readme_quick_example.py`](examples/readme_quick_example.py)

## Public API

Import from the package root:

See [`examples/api_and_model_package_surface.py`](examples/api_and_model_package_surface.py) for a runnable import example.

Primary entrypoints:
- `SysMLParser(path).parse()`
- `SysMLPackage.part_definitions`
- `SysMLPackage.port_definitions`
- `SysMLPackage.requirement_definitions`
- `container.defs(NodeType. ...)`
- `container.refs(NodeType. ...)`
- `container.add_def(...)`, `container.remove_def(...)`
- `container.add_ref(...)`, `container.remove_ref(...)`
- `architecture.export_flattened()`
- `architecture.export_declared()`

## Documentation

- [Getting Started](docs/getting_started.md): installation and common usage patterns
- [SysML Subset Reference](docs/syntax_reference.md): supported syntax
- [API and Data Model](docs/api_and_model.md): public classes and access patterns
- [Error Handling](docs/error_handling.md): parser exceptions and failure modes
- [Architecture Overview](docs/architecture_overview.md): internal parser flow and module responsibilities
- [Repository Layout](docs/layout.md): repository structure
- [Test Strategy](tests/README.md): test organization and conventions

## Development

Run tests with:

```bash
python -m pytest -q
```
