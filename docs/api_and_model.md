# API and Data Model

## Public API

```python
from pycps_sysmlv2 import load_architecture, load_system
from pycps_sysmlv2 import export_architecture, export_architecture_files
```

- `load_architecture(path)`:
  - folder path: parse all `*.sysml` in folder
  - file path: parse only that file
  - returns `SysMLArchitecture`
- `load_system(path, system_part)`:
  - convenience helper returning one part definition
- `export_architecture(architecture, mode="declared" | "flattened")`
- `export_architecture_files(architecture, mode="declared")`

## Top-Level Model

`SysMLArchitecture` contains:

- `package`
- `part_definitions`
- `port_definitions`
- `requirement_definitions`

## Core Definition Types

- `SysMLPartDefinition`
  - artifacts: attributes, ports, parts, connections, requirements
- `SysMLPortDefinition`
  - artifacts: attributes, requirements
- `SysMLRequirementDefinition`
  - artifacts: text

All definition types support:

- `specializes`
- `specializes_obj` (resolved base definition)
- `items`
- `redefines_items`
- `remove_items`

## Reference Types

- `SysMLPartReference`
- `SysMLPortReference`
- `SysMLRequirementReference`

References include both textual target names and resolved target objects (for example `port_def`, `part_def`, `requirement_def`).

## Inheritance Semantics

Inheritance for part/port/requirement definitions applies merge order:

1. `remove`
2. `redefines`
3. add declared items

Connection collisions require explicit remove first.

## Export Modes

- `declared`
  - preserves `specializes`, `redefines`, and `remove`
- `flattened`
  - emits effective merged members

`export_architecture_files(..., mode="declared")` groups output by `source_file` when available.
