"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: General-purpose helpers shared across package modules.
Design Notes:
- Keep utility behavior explicit and narrowly scoped to avoid hidden coupling.
- Prefer pure functions where possible to simplify testing and reuse.
Key Invariants:
- Utility functions should keep backward-compatible argument/return behavior.
- No utility should depend on filesystem or network side effects unless documented.
Strongly Connected External Modules:
- typing
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

def obj_base(obj):
    if isinstance(obj, list) and obj:
        if len(obj) == 0:
            return None
        return obj_base(obj[0])
    return obj

def obj_iterator(values):
    if isinstance(values, (list, tuple)):
        for i in values:
            yield i
    else:
        yield values







