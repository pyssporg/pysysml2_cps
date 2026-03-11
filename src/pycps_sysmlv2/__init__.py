"""Standalone SysML utilities package for architecture parsing and generation tooling."""

__version__ = "0.1.0"

from .definitions import (
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