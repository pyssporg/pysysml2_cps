# API and Data Model

## Package Surface

Import public classes from the package root:

See [`examples/api_and_model_package_surface.py`](../examples/api_and_model_package_surface.py).

## Main Entry Point

See [`examples/api_and_model_parsed_model.py`](../examples/api_and_model_parsed_model.py).

- `path` may be a single `.sysml` file or a directory
- the return type is `SysMLPackage`

## Top-Level Package Model

`SysMLPackage` exposes the parsed package through typed registries:

- `architecture.package`
- `architecture.part_definitions`
- `architecture.port_definitions`
- `architecture.requirement_definitions`

These properties are dictionary views over the generic definition container API:

See [`examples/api_and_model_parsed_model.py`](../examples/api_and_model_parsed_model.py).

## Definition Containers

Definition containers use:

- `defs(NodeType. ...)` for contained definitions
- `refs(NodeType. ...)` for contained references
- `add_def(type, key, obj)` / `remove_def(type, key)`
- `add_ref(type, key, obj)` / `remove_ref(type, key)`
- `get_def(type, key)`
- `get_ref(type, key)`

Supported container kinds:

- `SysMLPackage`
  - definitions: part, port, requirement
- `SysMLPartDefinition`
  - definitions: attribute, connection
  - references: part, port, requirement
- `SysMLPortDefinition`
  - definitions: attribute
  - references: requirement
- `SysMLRequirementDefinition`
  - definitions: attribute

Note:
- `SysMLPartDefinition.defs(NodeType.Part)` and `defs(NodeType.Port)` return effective inherited views because inheritance merges references into the resolved definition namespace.
- In practice, part subcomponents and ports should usually be accessed through `refs(...)`.

## Core Definition Types

- `SysMLPartDefinition`
  - `specializes`
  - `specializes_obj`
- `SysMLPortDefinition`
  - `specializes`
  - `specializes_obj`
- `SysMLRequirementDefinition`
  - `specializes`
  - `specializes_obj`
  - `text`

Requirement text is stored as the `text` attribute definition and exposed as a convenience property:

See [`examples/api_and_model_requirement_text.py`](../examples/api_and_model_requirement_text.py).

## Reference Types

Reference objects keep both the declared target name and the resolved target object:

- `SysMLPartReference`
  - `name`
  - `type`
  - `ref_node`
- `SysMLPortReference`
  - `name`
  - `direction`
  - `type`
  - `ref_node`
- `SysMLRequirementReference`
  - `name`
  - `type`
  - `ref_node`

## Connections

`SysMLConnection` stores both endpoint names and resolved endpoint nodes:

- `src_part`
- `src_port`
- `dst_part`
- `dst_port`
- `src_part_node`
- `dst_part_node`
- `src_port_node`
- `dst_port_node`
- `key`

Access connections from part definitions:

See [`examples/api_and_model_connection.py`](../examples/api_and_model_connection.py).

## Inheritance Semantics

Definition inheritance is resolved during parsing.

Merge order:

1. `remove`
2. `redefines`
3. declared additions

The resolved view is what `defs(...)` and `refs(...)` return on inherited definitions.

## Export

- `architecture.export_declared()`
  - returns `dict[str, str]`
  - groups output by source file
  - preserves `specializes`, `redefines`, and `remove`
- `architecture.export_flattened()`
  - returns `str`
  - emits the effective merged model

See [`examples/api_and_model_export.py`](../examples/api_and_model_export.py).

## Public vs Internal API

Members prefixed with `_` are internal implementation details.

External code, including tests, should use the documented public surface above rather than private storage like `_defs` or `_refs`.
