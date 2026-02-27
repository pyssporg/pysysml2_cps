from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .base import DefinitionBase
from .definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
)
from .references import SysMLRequirementReference


@dataclass(kw_only=True)
class SysMLArchitecture(DefinitionBase):
    package: str
    # keep port definitions before part definitions to ensure correct json export order
    port_definitions: Dict[str, SysMLPortDefinition] = field(default_factory=dict)
    part_definitions: Dict[str, SysMLPartDefinition] = field(default_factory=dict)
    requirement_definitions: Dict[str, SysMLRequirementDefinition] = field(default_factory=dict)

    def __post_init__(self):
        # sets json export order
        self.part_definitions = dict(
            sorted(
                self.part_definitions.items(),
                key=lambda item: (len(item[1].items.get("parts", {})), item[0]),
                reverse=False,
            )
        )
