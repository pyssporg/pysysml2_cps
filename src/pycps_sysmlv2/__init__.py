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
    SysMLRequirement,
    SysMLType,
)
from .exporter import SysMLExporter, export_architecture, export_architecture_files
from .parsing import SysMLFolderParser, load_architecture, load_system


from .parser_utils import json_dumps
