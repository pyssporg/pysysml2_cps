from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .base import DefinitionBase, NodeType


@dataclass(kw_only=True)
class SysMLPackage(DefinitionBase):
    package: str

    DEF_KINDS: tuple[NodeType, ...] = (
        NodeType.Part,
        NodeType.Port,
        NodeType.Requirement,
    )
    REF_KINDS: tuple[NodeType, ...] = tuple()

    # Export
    def export_flattened(self) -> str:
        from ..exporter import SysMLExporter

        return SysMLExporter().export_flattened(self)

    def export_declared(self) -> Dict[str, str]:
        from ..exporter import SysMLExporter

        return SysMLExporter().export_declared(self)
