# Architecture Overview

This document describes the internal parser pipeline and module responsibilities.

## Goals

- Parse a practical SysML v2 text subset from `*.sysml` files.
- Produce a connected in-memory architecture graph for Python tooling.
- Fail early with contextual validation errors when references cannot be resolved.

## Repository Structure

- `src/pycps_sysmlv2/` - package source
- `tests/` - unit and regression tests
- `docs/` - project documentation

## High-Level Flow

`SysMLParser(path).parse()` drives the full pipeline:

1. Normalize input path.
2. Parse either:
   - all `*.sysml` files in a folder, or
   - a single file if a file path is provided.
3. Extract packages, `part def`, `port def`, and requirements.
4. Build model objects (`SysMLPartDefinition`, `SysMLPortDefinition`, `SysMLRequirementDefinition`, and reference objects).
5. Resolve definition inheritance (parts, ports, requirements) with remove -> redefines -> add merge order.
6. Resolve references:
   - part ports -> port definitions
   - subpart instances -> part definitions
   - part/port requirement references -> requirement definitions
   - connections -> source/destination part and port definitions
7. Return one `SysMLPackage` object.

## Module Responsibilities

### `src/pycps_sysmlv2/__init__.py`

- Public package surface.
- Re-exports parser entrypoints and model classes.

### `src/pycps_sysmlv2/parser/`

- Parse orchestration and link-resolution passes.
- Main API:
  - `SysMLParser(folder_or_file).parse()`
- Internal responsibilities:
  - package extraction and consistency checks
  - block extraction (`part def`, `port def`, `requirement def`)
  - statement parsing (`attribute`, `in/out port`, `part`, `requirement`, `connect`, `redefines`, `remove`)
  - requirement handling: top-level definitions + in-block references
  - validation of unresolved references with contextual `ValueError`s

### `src/pycps_sysmlv2/inheritance.py`

- Isolated inheritance-resolution pass.
- Applies `remove -> redefines -> add` semantics for part/port/requirement definitions.
- Keeps parsed declared members separate from effective merged members.

### `src/pycps_sysmlv2/exporter.py`

- SysML text export.
- `architecture.export_declared()` preserves inheritance intent (`specializes`, `redefines`, `remove`) and groups definitions by recorded `source_file` when available.
- `architecture.export_flattened()` emits effective merged definitions.

### `src/pycps_sysmlv2/definitions/`

- Core domain model and type helpers.
- Main classes:
  - `SysMLPackage`
  - `SysMLPartDefinition`
  - `SysMLPortDefinition`
  - `SysMLRequirementDefinition`
  - `SysMLConnection`
  - `SysMLPartReference`
  - `SysMLPortReference`
  - `SysMLRequirementReference`
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

- Definitions (`part def`, `port def`, `requirement def`) are keyed dictionaries on `SysMLPackage`.
- References (`part`, `in/out port`, `requirement`) carry both:
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
  - requested definition/reference lookup not found via `get_def(...)` or `get_ref(...)`

## Supported Syntax (Subset)

See [SysML Subset Reference](syntax_reference.md) for the supported syntax surface.

## Extension Points

Common places to extend behavior:

- New statement forms:
  - update parsing helpers in `parser/builders.py` and `parser/elements.py`.
- Richer type system:
  - extend `PrimitiveType`, `SYSML_TYPE_MAP`, and `SysMLType`.
- Additional semantic validation:
  - add another validation pass after connection resolution.
- Better diagnostics:
  - add custom exception classes with file/line metadata.
- Additional export targets:
  - extend `exporter.py` with additional artifact emitters while reusing declared/effective views.
