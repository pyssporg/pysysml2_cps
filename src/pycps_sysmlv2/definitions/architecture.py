from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .base import DefinitionBase, NodeType
from .requirement_definition import SysMLRequirementDefinition
from .part_definition import SysMLPartDefinition
from .port_definition import SysMLPortDefinition


@dataclass(kw_only=True)
class SysMLPackage(DefinitionBase):
    package: str

    DEF_KINDS: tuple[NodeType, ...] = (
        NodeType.Part,
        NodeType.Port,
        NodeType.Requirement,
    )
    REF_KINDS: tuple[NodeType, ...] = tuple()

    @property
    def part_definitions(self) -> SysMLPartDefinition:
        return self.defs(NodeType.Part)

    @property
    def port_definitions(self) -> SysMLPortDefinition:
        return self.defs(NodeType.Port)

    @property
    def requirement_definitions(self) -> SysMLRequirementDefinition:
        return self.defs(NodeType.Requirement)

    # Export
    def export_flattened(self) -> str:
        from ..exporter import SysMLExporter

        return SysMLExporter().export_flattened(self)

    def export_declared(self) -> Dict[str, str]:
        from ..exporter import SysMLExporter

        return SysMLExporter().export_declared(self)
