from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .base import DefinitionBase


@dataclass
class SysMLRequirement(DefinitionBase):
    identifier: str
    text: str
    source_file: Optional[str] = None
