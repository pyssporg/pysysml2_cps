"""Data model definitions for lightweight SysML parsing."""

from .architecture import SysMLArchitecture
from .attributes import SysMLAttribute
from .base import DefinitionBase
from .declared import DeclaredDefinition
from .connections import SysMLConnection
from .parts import SysMLPartDefinition, SysMLPortDefinition
from .references import SysMLPartReference, SysMLPortReference
from .requirements import SysMLRequirement
from .types import PrimitiveType, SYSML_TYPE_MAP, SysMLType

__all__ = [
    "PrimitiveType",
    "SYSML_TYPE_MAP",
    "SysMLType",
    "DefinitionBase",
    "DeclaredDefinition",
    "SysMLAttribute",
    "SysMLRequirement",
    "SysMLConnection",
    "SysMLPortDefinition",
    "SysMLPartDefinition",
    "SysMLPartReference",
    "SysMLPortReference",
    "SysMLArchitecture",
]
