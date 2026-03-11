from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

from .base import InherenceDefinition
from .port_definition import SysMLPortDefinition
from .requirement_definition import SysMLRequirementDefinition
from .attributes import SysMLAttribute
from .connections import SysMLConnection
from .references import (
    SysMLPartReference,
    SysMLPortReference,
    SysMLRequirementReference,
)


@dataclass
class SysMLPartDefinition(InherenceDefinition):
    DEF_KINDS: tuple[str, ...] = (
        "attributes",
        "parts",
        "ports",
        "requirements",
        "connections",
    )
    REF_KINDS: tuple[str, ...] = (
        "parts",
        "ports",
        "requirements",
    )

    # Add ref
    def add_part_ref(self, key: str, reference: SysMLPartReference):
        self.add_ref(kind="parts", key=key, obj=reference)

    def add_port_ref(self, key: str, reference: SysMLPortReference):
        self.add_ref(kind="ports", key=key, obj=reference)

    def add_requirement_ref(self, key: str, reference: SysMLRequirementReference):
        self.add_ref(kind="requirements", key=key, obj=reference)

    # Remove ref
    def remove_part_ref(self, key: str):
        self.remove_ref(kind="parts", key=key)

    def remove_port_ref(self, key: str):
        self.remove_ref(kind="ports", key=key)

    def remove_requirement_ref(self, key: str):
        self.remove_ref(kind="requirements", key=key)

    # Get ref
    def get_part_ref(self, key: str):
        return self.get_ref(kind="parts", key=key)

    def get_port_ref(self, key: str):
        return self.get_ref(kind="ports", key=key)

    def get_requirement_ref(self, key: str):
        return self.get_ref(kind="requirements", key=key)

    # Add def
    def add_part_def(self, key: str, reference: SysMLPartDefinition):
        self.add_def(kind="parts", key=key, obj=reference)

    def add_port_def(self, key: str, reference: SysMLPortDefinition):
        self.add_def(kind="ports", key=key, obj=reference)

    def add_requirement_def(self, key: str, reference: SysMLPortDefinition):
        self.add_def(kind="requirements", key=key, obj=reference)

    def add_attributes_def(self, key: str, reference: SysMLAttribute):
        self.add_def(kind="attributes", key=key, obj=reference)

    def add_connections_def(self, reference: SysMLConnection):
        self.add_def(kind="connections", key=reference.key, obj=reference)

    # Remove def
    def remove_part_def(self, key: str):
        self.remove_def(kind="parts", key=key)

    def remove_port_def(self, key: str):
        self.remove_def(kind="ports", key=key)

    def remove_requirement_def(self, key: str):
        self.remove_def(kind="requirements", key=key)

    def remove_attributes_def(self, key: str):
        self.remove_def(kind="attributes", key=key)

    def remove_connections_def(self, key: str):
        self.remove_def(kind="connections", key=key)

    # Get def
    def get_part_def(self, key: str):
        return self.get_def(kind="parts", key=key)

    def get_port_def(self, key: str):
        return self.get_def(kind="ports", key=key)

    def get_requirement_def(self, key: str):
        return self.get_def(kind="requirements", key=key)

    def get_attributes_def(self, key: str):
        return self.get_def(kind="attributes", key=key)

    def get_connections_def(self, key: str):
        return self.get_def(kind="connections", key=key)

    @property
    def connections(self) -> list[object]:
        return list(self.refs["connections"].values())
