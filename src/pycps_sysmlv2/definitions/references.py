from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import DefinitionBase


@dataclass(kw_only=True)
class SysMLPartReference(DefinitionBase):
    name: str
    part_name: str
    doc: Optional[str] = None
    part_def: Optional["SysMLPartDefinition"] = None


@dataclass(kw_only=True)
class SysMLPortReference(DefinitionBase):
    name: str
    direction: str  # "in" or "out"
    port_name: str
    doc: Optional[str] = None
    port_def: Optional["SysMLPortDefinition"] = None
