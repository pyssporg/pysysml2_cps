from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import DefinitionBase
from .definitions import SysMLPartDefinition, SysMLPortDefinition, SysMLRequirementDefinition


@dataclass(kw_only=True)
class SysMLPartReference(DefinitionBase):
    part_name: str
    part_def: Optional[SysMLPartDefinition] = None


@dataclass(kw_only=True)
class SysMLPortReference(DefinitionBase):
    direction: str  # "in" or "out"
    port_name: str
    port_def: Optional[SysMLPortDefinition] = None


@dataclass(kw_only=True)
class SysMLRequirementReference(DefinitionBase):
    requirement_name: str
    requirement_def: Optional[SysMLRequirementDefinition] = None

    @property
    def identifier(self) -> str:
        return self.name

    @property
    def text(self) -> str:
        if self.requirement_def is None:
            return ""
        return self.requirement_def.text
