"""Data model definitions for lightweight SysML parsing."""

from .architecture import SysMLArchitecture
from .attributes import SysMLAttribute
from .base import DeclaredDefinition, DefinitionBase
from .connections import SysMLConnection
from .definitions import (
    ResolvedPartDefinition,
    ResolvedPortDefinition,
    ResolvedRequirement,
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
    "DefinitionBase",
    "DeclaredDefinition",
    "SysMLAttribute",
    "ResolvedRequirement",
    "SysMLRequirement",
    "SysMLConnection",
    "ResolvedPortDefinition",
    "SysMLPortDefinition",
    "ResolvedPartDefinition",
    "SysMLPartDefinition",
    "SysMLPartReference",
    "SysMLPortReference",
    "SysMLArchitecture",
]
