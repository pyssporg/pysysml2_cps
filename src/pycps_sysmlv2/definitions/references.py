from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import SysMLBase
from .part_definition import SysMLPartDefinition
from .port_definition import SysMLPortDefinition
from .requirement_definition import SysMLRequirementDefinition


@dataclass(kw_only=True)
class SysMLPartReference(SysMLBase):
    part_name: str
    part_def: Optional[SysMLPartDefinition] = None


@dataclass(kw_only=True)
class SysMLPortReference(SysMLBase):
    direction: str  # "in" or "out"
    port_name: str
    port_def: Optional[SysMLPortDefinition] = None


@dataclass(kw_only=True)
class SysMLRequirementReference(SysMLBase):
    requirement_name: str
    requirement_def: Optional[SysMLRequirementDefinition] = None

    # TODO: Remove, easier to inline
    @property
    def identifier(self) -> str:
        return self.name

    # TODO: Remove, access the requirement_def directly
    @property
    def text(self) -> str:
        if self.requirement_def is None:
            return ""
        return self.requirement_def.text
