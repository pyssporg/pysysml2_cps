# Architecture Overview

This document describes how `pycps_sysmlv2` is structured so development decisions and extension points are explicit.

## Goals

- Parse a practical SysML v2 text subset from `*.sysml` files.
- Produce a connected in-memory architecture graph for Python tooling.
- Fail early with contextual validation errors when references cannot be resolved.

## Repository Structure

- `src/pycps_sysmlv2/` - package source
- `tests/` - unit and regression tests
- `examples/` - runnable usage example
- `docs/` - project documentation

## High-Level Flow

`load_architecture(path)` drives the full pipeline:

1. Normalize input path.
2. Parse either:
   - all `*.sysml` files in a folder, or
   - a single file if a file path is provided.
3. Extract packages, `part def`, `port def`, and requirements.
4. Build model objects (`SysMLPartDefinition`, `SysMLPortDefinition`, etc.).
5. Resolve part inheritance (remove -> redefines -> add merge order).
6. Resolve references:
   - part ports -> port definitions
   - subpart instances -> part definitions
   - connections -> source/destination part and port definitions
7. Return one `SysMLArchitecture` object.

## Module Responsibilities

### `src/pycps_sysmlv2/__init__.py`

- Public package surface.
- Re-exports parser entrypoints and model classes.

### `src/pycps_sysmlv2/parsing.py`

- Parse orchestration and link-resolution passes.
- Main APIs:
  - `load_architecture(folder_or_file)`
  - `load_system(folder_or_file, system_part)`
- Internal responsibilities:
  - package extraction and consistency checks
  - block extraction (`part def`, `port def`)
  - statement parsing (`attribute`, `in/out port`, `part`, `connect`, `redefines`, `remove`)
  - requirement extraction (`requirement def`, `requirement ... : ...;`)
  - validation of unresolved references with contextual `ValueError`s

### `src/pycps_sysmlv2/definitions.py`

- Core domain model and type helpers.
- Main classes:
  - `SysMLArchitecture`
  - `SysMLPartDefinition`
  - `SysMLPortDefinition`
  - `SysMLConnection`
  - `SysMLRequirement`
  - `SysMLPartReference`
  - `SysMLPortReference`
  - `SysMLType` / `PrimitiveType`
- Also includes literal-to-type inference for attributes.

### `src/pycps_sysmlv2/parser_utils.py`

- Low-level parser helpers:
  - brace-balanced block collection
  - inline/doc comment normalization
  - recursive JSON serialization helpers for model inspection/debugging

### `src/pycps_sysmlv2/utils.py`

- Small generic helpers used by typing/model code.

## Data Model Design

The parser intentionally returns a resolved object graph, not only raw syntax.

- Definitions (`part def`, `port def`) are keyed dictionaries on `SysMLArchitecture`.
- References (`part`, `in/out port`) carry both:
  - raw textual target names
  - resolved object links (or fail during load if missing)
- Connections store endpoint names plus resolved endpoint definitions.

This supports downstream tooling without repeated name lookups.

## Validation and Error Behavior

The parser validates during load rather than deferring failures:

- `FileNotFoundError`:
  - missing input folder
  - no `.sysml` files in folder
- `ValueError`:
  - missing package declaration
  - package mismatch across files
  - duplicate definitions
  - malformed declarations
  - unresolved port/part references
  - unresolved connection endpoints
- `KeyError`:
  - requested `load_system(..., system_part)` not found

## Supported Syntax (Subset)

- `package Name { ... }`
- `part def Name { ... }`
- `part def Derived specializes Base { ... }`
- `port def Name { ... }`
- `attribute name = literal;`
- `attribute name: Type;`
- `in port p : PortType;`
- `out port p : PortType;`
- `part child : PartDef;`
- `connect a.port to b.port;`
- `redefines attribute|in/out port|part ...`
- `remove attribute|port|part|connect ...`
- `doc /* ... */`
- `requirement def RequirementName { ... }`
- `requirement ReqId : RequirementName;`

Non-goals currently include full SysML v2 language coverage and behavioral semantics.

## Extension Points

Common places to extend behavior:

- New statement forms:
  - update `_iter_block_items(...)` and parsing helpers in `parsing.py`.
- Richer type system:
  - extend `PrimitiveType`, `SYSML_TYPE_MAP`, and `SysMLType`.
- Additional semantic validation:
  - add another validation pass after connection resolution.
- Better diagnostics:
  - add custom exception classes with file/line metadata.

## Testing Strategy

- `tests/test_public_api_*.py`: split public API behavior by concern.
- `tests/test_type_utils.py`: typing/literal inference behavior.
- `tests/test_error_handling.py`: failure mode and error-message regression coverage.

Run tests with:

```bash
python -m pytest -q
```
