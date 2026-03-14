"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Parser package export surface.
Design Notes:
- Expose SysMLParser as the primary entrypoint for loading models.
- Avoid leaking low-level parser internals through package exports.
Key Invariants:
- Importing parser package must not trigger file IO or parsing side effects.
- Exported parser symbols must remain compatible with package-level imports.
Strongly Connected External Modules:
- pycps_sysmlv2.parser.loader
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from .loader import SysMLParser

__all__ = ["SysMLParser"]
