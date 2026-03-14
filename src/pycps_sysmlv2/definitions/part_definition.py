"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Part definition model and helpers for owned members.
Design Notes:
- Model parts with nested ports/attributes/connections for rich architecture graphs.
- Keep ownership semantics explicit via parent relationships.
Key Invariants:
- Part member collections must preserve deterministic iteration order.
- Specialization references should remain explicit strings until resolution.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions.attributes
- pycps_sysmlv2.definitions.connections
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

from dataclasses import dataclass

from .base import InherenceDefinition, NodeType


@dataclass
class SysMLPartDefinition(InherenceDefinition):
    DEF_KINDS: tuple[NodeType, ...] = (
        NodeType.Attribute,
        NodeType.Part,
        NodeType.Port,
        NodeType.Requirement,
        NodeType.Connection,
    )
    REF_KINDS: tuple[NodeType, ...] = (
        NodeType.Part,
        NodeType.Port,
        NodeType.Requirement,
    )


