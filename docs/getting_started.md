# Getting Started

## Requirements

- Python 3.10 or newer

## Install

From the repository root:

```bash
pip install -e .
```

## Load a Model

Parse either a single file or a directory of `.sysml` files:

See [`examples/getting_started_load_model.py`](../examples/getting_started_load_model.py).

When given a directory, the parser loads all `*.sysml` files in that directory and merges them into one package model.

## Inspect Definitions

Top-level definitions are exposed as dictionaries:

See [`examples/getting_started_inspect_definitions.py`](../examples/getting_started_inspect_definitions.py).

## Inspect Members

Use `defs(...)` for declared artifacts and `refs(...)` for references:

See [`examples/getting_started_inspect_members.py`](../examples/getting_started_inspect_members.py).

## Follow Resolved References

References include both the textual target name and the resolved definition object:

See [`examples/getting_started_follow_references.py`](../examples/getting_started_follow_references.py).

## Walk Connections

See [`examples/getting_started_walk_connections.py`](../examples/getting_started_walk_connections.py).

## Export SysML

See [`examples/getting_started_export_sysml.py`](../examples/getting_started_export_sysml.py).

- `export_declared()` preserves `specializes`, `redefines`, and `remove`
- `export_flattened()` emits the effective merged model

## Next Reading

- [SysML Subset Reference](syntax_reference.md)
- [API and Data Model](api_and_model.md)
- [Error Handling](error_handling.md)
