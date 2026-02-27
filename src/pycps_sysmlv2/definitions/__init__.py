"""Data model definitions for lightweight SysML parsing."""

from .architecture import SysMLArchitecture
from .attributes import SysMLAttribute
from .connections import SysMLConnection
from .definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirement,
)
from .references import SysMLPartReference, SysMLPortReference
from .types import PrimitiveType, SYSML_TYPE_MAP, SysMLType

__all__ = [
    "PrimitiveType",
    "SYSML_TYPE_MAP",
    "SysMLType",
    "SysMLAttribute",
    "SysMLRequirement",
    "SysMLConnection",
    "SysMLPortDefinition",
    "SysMLPartDefinition",
    "SysMLPartReference",
    "SysMLPortReference",
    "SysMLArchitecture",
]
