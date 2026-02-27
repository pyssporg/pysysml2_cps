"""Data model definitions for lightweight SysML parsing."""

from .architecture import SysMLArchitecture
from .attributes import SysMLAttribute
from .connections import SysMLConnection
from .definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirement,
    SysMLRequirementDefinition,
)
from .references import SysMLPartReference, SysMLPortReference, SysMLRequirementReference
from .types import PrimitiveType, SYSML_TYPE_MAP, SysMLType

__all__ = [
    "PrimitiveType",
    "SYSML_TYPE_MAP",
    "SysMLType",
    "SysMLAttribute",
    "SysMLConnection",
    "SysMLRequirement",
    "SysMLRequirementDefinition",
    "SysMLPortDefinition",
    "SysMLPartDefinition",
    "SysMLPartReference",
    "SysMLPortReference",
    "SysMLRequirementReference",
    "SysMLArchitecture",
]
