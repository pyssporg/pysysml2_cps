from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .declared import DeclaredDefinition


@dataclass
class SysMLRequirement(DeclaredDefinition):
    identifier: str
    text: str
