# Traceability Preamble Template

Use this preamble at the top of each Python source module to capture purpose and design intent in a consistent, grep-friendly format.

```python
"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: <Short statement of what this module owns>.
Design Notes:
- <Constraint or guiding principle that shaped this module.>
- <Tradeoff that maintainers should preserve or revisit intentionally.>
Key Invariants:
- <Behavior that must stay stable unless intentionally changed.>
- <Another contract relied on by tests, callers, or tooling.>
Strongly Connected External Modules:
- <External or sibling module with tight coupling to this module's behavior.>
- <Second strongly connected module, if applicable.>
Decision Log:
- <YYYY-MM-DD>: <Behavior-affecting design decision and rationale.>
"""
```

## Field guidance

- `Purpose`: keep this short; no strict format beyond a concise ownership statement.
- `Design Notes`: explain constraints, tradeoffs, or boundaries.
- `Key Invariants`: capture contracts and assumptions that should remain stable.
- `Strongly Connected External Modules`: list modules/packages this file is tightly coupled to so ripple effects are visible during refactors.
- `Decision Log`: record only behavior-affecting decisions worth revisiting later.

## Suggested update workflow

1. Add/update the preamble when creating or refactoring a module.
2. Keep `Decision Log` entries short and append-only.
3. If behavior changes materially, append a dated entry; avoid logging metadata-only edits.
4. Bump `Template Version` only when preamble field semantics or required sections change.
