# API and Data Model

## Public API

```python
from pycps_sysmlv2 import SysMLParser
```

- `SysMLParser(path).parse()`:
  - folder path: parse all `*.sysml` in folder
  - file path: parse only that file
  - returns `SysMLArchitecture`
- `architecture.get_part(system_part)`:
  - convenience helper returning one part definition
- `architecture.export_flattened()`
- `architecture.export_declared()`

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

## Export Functions

- `architecture.export_declared()`
  - preserves `specializes`, `redefines`, and `remove`
  - groups output by `source_file` when available
- `architecture.export_flattened()`
  - emits effective merged members
