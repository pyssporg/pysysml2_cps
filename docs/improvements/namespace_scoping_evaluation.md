# Namespace-Level Definitions Evaluation

This note evaluates how namespace-level definitions could work in `pycps_sysmlv2`, with a path toward supporting artifacts defined inside parts.

## Goal

Enable references like:

- `system_def.add_requirement("reqA", "ReqA")`
- `system_def.add_connection("child", "out", "child", "in")`

without requiring explicit `*_def` arguments, while still resolving and filling those links automatically.

Longer-term goal: support artifacts defined inside parts with predictable name resolution.

## Recommended Conceptual Model

Use hierarchical scopes (namespaces):

- `PackageScope` (root)
- `PartScope` (child of package or another part)
- `PortScope` (optional future extension)

Each scope owns symbol tables for definitions:

- `part_definitions`
- `port_definitions`
- `requirement_definitions`

Each definition carries:

- `name` (local symbol)
- `qualified_name` (for example `Pkg::System::InnerPart`)
- `owner_scope` (the scope that declares it)

## Resolution Semantics

For unqualified references (`ReqA`, `Signal`, `ChildType`):

1. Resolve in current scope.
2. If not found, walk parent scopes upward.
3. Optionally evaluate explicit imports/aliases (future).
4. If multiple matches remain, raise ambiguity error with candidates.
5. If unresolved and non-strict mode is enabled, allow deferred resolution.

This gives lexical scoping and naturally enables artifacts defined inside parts.

## API Implications

With scope ownership in place, mutators can auto-resolve:

- `add_requirement(name, requirement_name, requirement_def=None)`:
  - If `requirement_def` omitted, resolve by `requirement_name` using owner scope.
- `add_connection(src_component, src_port, dst_component, dst_port, ...)`:
  - Resolve source/destination subpart refs from current part scope.
  - Resolve endpoint port definitions from resolved part definitions.

Suggested strictness behavior:

- `strict=True` (default): raise contextual `ValueError` on unresolved or ambiguous symbols.
- `strict=False`: keep unresolved links as `None` and permit deferred resolution.

## Migration Path

1. Add ownership metadata:
   - `owner_scope` (or initially `owner_architecture`) on definitions/references.
2. Introduce `Scope` abstraction while preserving current package-level behavior.
3. Centralize lookup logic in resolver helpers:
   - `resolve_requirement_ref(...)`
   - `resolve_connection_endpoints(...)`
4. Update parser to build scope tree and attach nested definitions.
5. Add support for nested artifact declarations in syntax/parsing.
6. Add ambiguity diagnostics and qualified-name handling.
7. Update exporter and JSON serialization for scoped names where needed.

## Tradeoffs

Pros:

- Clear and extensible name resolution model.
- Direct support for nested artifacts inside parts.
- Cleaner mutator API with optional auto-resolution.

Costs:

- Increased parser/model complexity.
- Need explicit ambiguity policies and diagnostics.
- Potential exporter/reference-format updates.

## Suggested Next Implementation Slice

Implement a minimal first slice:

- Add `owner_architecture`/`owner_scope` linkage.
- Add centralized resolver helpers.
- Make `add_requirement` and `add_connection` auto-resolve when optional defs are omitted.
- Add strict/non-strict behavior tests.

This captures most immediate value with low disruption, and keeps future nested-scope support straightforward.
