from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .base import InherenceDefinition
from .requirement_definition import SysMLRequirementDefinition


@dataclass
class SysMLPortDefinition(InherenceDefinition):
    pass
