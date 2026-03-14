"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Package export surface for parser, model definitions, and helpers.
Design Notes:
- Keep imports curated so top-level API remains stable and discoverable.
- Avoid re-exporting internal parser helpers that bypass validation pathways.
Key Invariants:
- Names listed in __all__ must resolve and remain import-safe for callers/tests.
- Version and export ordering should change only with intentional API updates.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions
- pycps_sysmlv2.parser
- pycps_sysmlv2.parser_utils
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
__version__ = "0.1.0"

from .definitions import (
    PrimitiveType,
    NodeType,
    SYSML_TYPE_MAP,
    SysMLPackage,
    SysMLAttribute,
    SysMLConnection,
    SysMLPartDefinition,
    SysMLPartReference,
    SysMLPortDefinition,
    SysMLPortReference,
    SysMLRequirementDefinition,
    SysMLRequirementReference,
    SysMLType,
)

from .parser import SysMLParser

from .parser_utils import json_dumps

__all__ = [
    "PrimitiveType",
    "NodeType",
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
    "SysMLParser",
]
