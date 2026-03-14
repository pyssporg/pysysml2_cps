"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Reference node models for parts, ports, and requirements.
Design Notes:
- Keep references lightweight wrappers that point to resolved definitions.
- Preserve raw target names to support deferred linking workflows.
Key Invariants:
- Reference objects must retain target identity text for error reporting.
- Resolved pointers should be optional until linker phase completes.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions.base
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

from dataclasses import dataclass

from .base import ReferenceBase

# TODO: utilize the reference base class
# map name to type and x_def to definition

@dataclass(kw_only=True)
class SysMLPartReference(ReferenceBase):
    pass


@dataclass(kw_only=True)
class SysMLPortReference(ReferenceBase):
    direction: str  # "in" or "out"


@dataclass(kw_only=True)
class SysMLRequirementReference(ReferenceBase):
    pass
