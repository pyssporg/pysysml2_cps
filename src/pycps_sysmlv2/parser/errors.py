"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Parser-specific exception types and error formatting helpers.
Design Notes:
- Encode file/line context in exceptions to simplify debugging input models.
- Differentiate syntax and linkage failures with distinct exception classes.
Key Invariants:
- Error classes should remain stable for callers asserting failure modes.
- Messages must include enough context to locate invalid source quickly.
Strongly Connected External Modules:
- pathlib
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

from pathlib import Path


def unknown_statement_error(
    package_name: str,
    source_path: Path,
    definition_kind: str,
    definition_name: str,
    line: str,
) -> ValueError:
    return ValueError(
        "Unknown statement while parsing "
        f"{definition_kind} {definition_name} in package {package_name} "
        f"({source_path}): {line}"
    )
