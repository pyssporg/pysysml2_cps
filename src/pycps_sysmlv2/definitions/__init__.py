"""Data model definitions for lightweight SysML parsing."""

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
