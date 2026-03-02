"""Standalone SysML utilities package for architecture parsing and generation tooling."""

__version__ = "0.1.0"

from .definitions import (
    SysMLArchitecture,
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
from .exporter import (
    SysMLExporter,
)
from .parser import SysMLParser

from .parser_utils import json_dumps
