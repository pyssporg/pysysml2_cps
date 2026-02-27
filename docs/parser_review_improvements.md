# Parser Review: Improvement Backlog

Date: 2026-02-27

This file captures follow-up improvements identified while reviewing tests and parser behavior against expected module function and SysML v2 alignment.

## 1. Redefine and and isolate project-specific DSL features

Implement support for standard compliant syntax specializes, redefines 
Keep the `remove ...` syntax

- Document clearly that `remove ...` inheritance mutations are project-specific shorthand and not standard SysML v2 textual notation.
- Add a dedicated section in `README.md` and API docs distinguishing:
  - supported "subset" constructs
  - custom extensions
  - intentionally unsupported SysML v2 constructs

## 2. Requirement modeling semantics

- Current behavior parses requirements from `comment <ID> /* ... */`.
- Add support (or at least explicit rejection with clear errors) for SysML v2 requirement constructs (`requirement def` / usage-style statements).
- Remove comment-based extraction.

## 3. Strict parsing mode for unknown statements

- Current part/port block parsing silently ignores unrecognized statements.
- Add a strict mode (default recommended) that raises a `ValueError` on unknown statement lines with context:
  - file
  - package
  - enclosing definition
  - offending line

## 4. Loader behavior clarity

- `load_architecture(path_to_file)` currently parses the parent folder, not only that file.
- ensure that when a file is defined, it does not load the entire parent folder


## 6. Value/type parsing semantics

- Current attribute literal parsing uses Python `ast.literal_eval`.
- Add explicit limitations in docs (Python-literal-based parsing, no full SysML expression evaluation).

## 7. Internal implementation cleanup

- Remove redundant base checks (`_attach_base_part_definitions` overlaps with `_resolve_part_inheritance` checks).
- Remove unused `ports` parameter from `_attach_connection_definitions`.
- Fix typing mismatch in `_parse_attribute` (`attr_type` should be `Optional[SysMLType]`).
- Add targeted unit tests for these internals where behavior changes.

## 8. Test coverage follow-ups

- Update tests regarding adjusted functionality
