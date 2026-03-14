"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Requirement definition model and requirement text metadata.
Design Notes:
- Store requirement statements and hierarchy for compliance modeling.
- Support specialization chains used in inheritance resolution.
Key Invariants:
- Requirement text/content should remain unchanged by linking/export routines.
- Specialization references must be explicit and deterministic.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions.base
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

from dataclasses import dataclass

from .base import InherenceDefinition, NodeType
from .attributes import SysMLAttribute


@dataclass
class SysMLRequirementDefinition(InherenceDefinition):
    DEF_KINDS: tuple[NodeType, ...] = (NodeType.Attribute,)
    REF_KINDS: tuple[NodeType, ...] = tuple()

    @property
    def text(self) -> str:
        value = self.get_def(NodeType.Attribute, "text").value
        return str(value)

    @text.setter
    def text(self, value) -> str:
        attrib = SysMLAttribute.from_literal(name="text", value=value, doc=None )
        self.add_def(NodeType.Attribute, "text", attrib)