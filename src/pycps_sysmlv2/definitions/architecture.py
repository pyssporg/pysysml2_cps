from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Dict

from .base import SysMLBase
from .part_definition import SysMLPartDefinition
from .port_definition import SysMLPortDefinition
from .requirement_definition import SysMLRequirementDefinition


@dataclass(kw_only=True)
class SysMLArchitecture(SysMLBase):
    package: str
    # keep port definitions before part definitions to ensure correct json export order
    port_definitions: Dict[str, SysMLPortDefinition] = field(default_factory=dict)
    part_definitions: Dict[str, SysMLPartDefinition] = field(default_factory=dict)
    requirement_definitions: Dict[str, SysMLRequirementDefinition] = field(
        default_factory=dict
    )

    def __post_init__(self):
        # sets json export order
        self.part_definitions = dict(
            sorted(
                self.part_definitions.items(),
                key=lambda item: (len(item[1].refs.get("parts", {})), item[0]),
                reverse=False,
            )
        )

    def get_part(self, part_name: str) -> SysMLPartDefinition:
        if part_name not in self.part_definitions:
            raise KeyError(f"Part not found: {part_name}")
        return self.part_definitions[part_name]

    def add_part(self, definition: SysMLPartDefinition) -> SysMLPartDefinition:
        if definition.name in self.part_definitions:
            warnings.warn(
                f"Overwriting existing part definition: {definition.name}",
                UserWarning,
                stacklevel=2,
            )
        self.part_definitions[definition.name] = definition
        return definition

    def remove_part(self, part_name: str) -> SysMLPartDefinition:
        if part_name not in self.part_definitions:
            raise KeyError(f"Part not found: {part_name}")
        return self.part_definitions.pop(part_name)

    def get_port(self, port_name: str) -> SysMLPortDefinition:
        if port_name not in self.port_definitions:
            raise KeyError(f"Port not found: {port_name}")
        return self.port_definitions[port_name]

    def add_port(self, definition: SysMLPortDefinition) -> SysMLPortDefinition:
        if definition.name in self.port_definitions:
            warnings.warn(
                f"Overwriting existing port definition: {definition.name}",
                UserWarning,
                stacklevel=2,
            )
        self.port_definitions[definition.name] = definition
        return definition

    def remove_port(self, port_name: str) -> SysMLPortDefinition:
        if port_name not in self.port_definitions:
            raise KeyError(f"Port not found: {port_name}")
        return self.port_definitions.pop(port_name)

    def get_requirement(self, req_name: str) -> SysMLRequirementDefinition:
        if req_name not in self.requirement_definitions:
            raise KeyError(f"Requirement not found: {req_name}")
        return self.requirement_definitions[req_name]

    def add_requirement(
        self, definition: SysMLRequirementDefinition
    ) -> SysMLRequirementDefinition:
        if definition.name in self.requirement_definitions:
            warnings.warn(
                f"Overwriting existing requirement definition: {definition.name}",
                UserWarning,
                stacklevel=2,
            )
        self.requirement_definitions[definition.name] = definition
        return definition

    def remove_requirement(self, req_name: str) -> SysMLRequirementDefinition:
        if req_name not in self.requirement_definitions:
            raise KeyError(f"Requirement not found: {req_name}")
        return self.requirement_definitions.pop(req_name)

    def export_flattened(self) -> str:
        from ..exporter import SysMLExporter

        return SysMLExporter().export_flattened(self)

    def export_declared(self) -> Dict[str, str]:
        from ..exporter import SysMLExporter

        return SysMLExporter().export_declared(self)
