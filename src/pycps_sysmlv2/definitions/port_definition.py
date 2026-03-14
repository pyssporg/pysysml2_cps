"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Port definition model and port-specific semantics.
Design Notes:
- Represent direction/type metadata needed for parser validation and export.
- Support inheritance-friendly storage of owned attributes.
Key Invariants:
- Port direction and type strings must remain intact through parse/export cycle.
- Port attribute inheritance should not overwrite local declarations silently.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions.attributes
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

from dataclasses import dataclass

from .base import InherenceDefinition, NodeType


@dataclass
class SysMLPortDefinition(InherenceDefinition):
    DEF_KINDS: tuple[NodeType, ...] = (NodeType.Attribute,NodeType.Requirement,)
    REF_KINDS: tuple[NodeType, ...] = (NodeType.Requirement,)

