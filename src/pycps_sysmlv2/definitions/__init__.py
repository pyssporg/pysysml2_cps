"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Definitions package export surface for model node types.
Design Notes:
- Re-export dataclasses used by parser, exporter, and consumers.
- Keep this module synchronized with concrete definition modules.
Key Invariants:
- Exported symbols must map to actual dataclass/enum implementations.
- Changes here are API changes and should be intentional.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions.*
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from .architecture import SysMLPackage
from .attributes import SysMLAttribute
from .connections import SysMLConnection
from .part_definition import SysMLPartDefinition
from .port_definition import SysMLPortDefinition
from .requirement_definition import SysMLRequirementDefinition
from .references import SysMLPartReference, SysMLPortReference, SysMLRequirementReference
from .types import PrimitiveType, SYSML_TYPE_MAP, SysMLType
from .base import NodeType

__all__ = [
    "PrimitiveType",
    "SYSML_TYPE_MAP",
    "SysMLType",
    "SysMLAttribute",
    "SysMLConnection",
    "SysMLRequirementDefinition",
    "SysMLPortDefinition",
    "SysMLPartDefinition",
    "SysMLPartReference",
    "SysMLPortReference",
    "SysMLRequirementReference",
    "SysMLPackage",
    "NodeType"
]
