from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import SysMLBase, ReferenceBase
from .part_definition import SysMLPartDefinition
from .port_definition import SysMLPortDefinition
from .requirement_definition import SysMLRequirementDefinition

# TODO: utilize the reference base class
# map name to type and x_def to definition

@dataclass(kw_only=True)
class SysMLPartReference(ReferenceBase):
    pass


@dataclass(kw_only=True)
class SysMLPortReference(ReferenceBase):
    direction: str  # "in" or "out"


@dataclass(kw_only=True)
class SysMLRequirementReference(ReferenceBase):
    pass
