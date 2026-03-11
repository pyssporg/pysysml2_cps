from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Dict

from .base import SysMLBase, DefinitionBase
from .part_definition import SysMLPartDefinition
from .port_definition import SysMLPortDefinition
from .requirement_definition import SysMLRequirementDefinition


@dataclass(kw_only=True)
class SysMLPackage(DefinitionBase):
    package: str

    DEF_KINDS: tuple[str, ...] = (
        "parts",
        "ports",
        "requirements",
    )
    REF_KINDS: tuple[str, ...] = tuple()

    # Add def
    def add_part_def(self, key: str, reference: SysMLPartDefinition):
        self.add_def(kind="parts", key=key, obj=reference)

    def add_port_def(self, key: str, reference: SysMLPortDefinition):
        self.add_def(kind="ports", key=key, obj=reference)

    def add_requirement_def(self, key: str, reference: SysMLPortDefinition):
        self.add_def(kind="requirement", key=key, obj=reference)

    # Remove def
    def remove_part_def(self, key: str):
        self.remove_def(kind="parts", key=key)

    def remove_port_def(self, key: str):
        self.remove_def(kind="ports", key=key)

    def remove_requirement_def(self, key: str):
        self.remove_def(kind="requirement", key=key)

    # Get def
    def get_part_def(self, key: str):
        return self.get_def(kind="parts", key=key)

    def get_port_def(self, key: str):
        return self.get_def(kind="ports", key=key)

    def get_requirement_def(self, key: str):
        return self.get_def(kind="requirements", key=key)

    # Export
    def export_flattened(self) -> str:
        from ..exporter import SysMLExporter

        return SysMLExporter().export_flattened(self)

    def export_declared(self) -> Dict[str, str]:
        from ..exporter import SysMLExporter

        return SysMLExporter().export_declared(self)
