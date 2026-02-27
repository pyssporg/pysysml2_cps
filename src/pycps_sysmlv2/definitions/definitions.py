from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .attributes import SysMLAttribute
from .connections import SysMLConnection
from .declared import DeclaredDefinition
from .references import SysMLPartReference, SysMLPortReference



@dataclass
class SysMLRequirement(DeclaredDefinition):
    identifier: str
    text: str
    artifact_kinds: Tuple[str, ...] = ("text",)


@dataclass
class SysMLPortDefinition(DeclaredDefinition):
    name: str
    doc: Optional[str] = None
    attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    artifact_kinds: Tuple[str, ...] = ("attributes",)


@dataclass
class SysMLPartDefinition(DeclaredDefinition):
    name: str
    doc: Optional[str] = None
    base_part_name: Optional[str] = None
    base_part_def: Optional["SysMLPartDefinition"] = None
    source_file: Optional[str] = None
    attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    ports: Dict[str, SysMLPortReference] = field(default_factory=dict)
    parts: Dict[str, SysMLPartReference] = field(default_factory=dict)
    connections: List[SysMLConnection] = field(default_factory=list)
    declared_attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    declared_ports: Dict[str, SysMLPortReference] = field(default_factory=dict)
    declared_parts: Dict[str, SysMLPartReference] = field(default_factory=dict)
    declared_connections: List[SysMLConnection] = field(default_factory=list)
    replace_attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    replace_ports: Dict[str, SysMLPortReference] = field(default_factory=dict)
    replace_parts: Dict[str, SysMLPartReference] = field(default_factory=dict)
    remove_attributes: Set[str] = field(default_factory=set)
    remove_ports: Set[str] = field(default_factory=set)
    remove_parts: Set[str] = field(default_factory=set)
    remove_connections: List[SysMLConnection] = field(default_factory=list)
    artifact_kinds: Tuple[str, ...] = ("attributes", "ports", "parts", "connections")
    items: Dict[str, Dict[str, object]] = field(default_factory=dict)
    redefines_items: Dict[str, Dict[str, object]] = field(default_factory=dict)
    remove_items: Dict[str, set[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._init_declared_maps()
        self.items["attributes"] = dict(self.declared_attributes or self.attributes)
        self.items["ports"] = dict(self.declared_ports or self.ports)
        self.items["parts"] = dict(self.declared_parts or self.parts)
        self.items["connections"] = {
            _connection_key(c): c for c in (self.declared_connections or self.connections)
        }

        self.redefines_items["attributes"] = dict(self.replace_attributes)
        self.redefines_items["ports"] = dict(self.replace_ports)
        self.redefines_items["parts"] = dict(self.replace_parts)

        self.remove_items["attributes"] = set(self.remove_attributes)
        self.remove_items["ports"] = set(self.remove_ports)
        self.remove_items["parts"] = set(self.remove_parts)
        self.remove_items["connections"] = {_connection_key(c) for c in self.remove_connections}

    def get_port_attributes(
        self,
    ) -> List[Tuple[SysMLPortReference, SysMLPortDefinition, SysMLAttribute]]:
        attributes = []
        for port in self.ports.values():
            port_def = port.port_def
            if port_def is None:
                raise ValueError(
                    f"Port definition not resolved for {self.name}.{port.name} ({port.port_name})"
                )
            for attr in port_def.attributes.values():
                attributes.append((port, port_def, attr))
        return attributes


def _connection_key(connection: SysMLConnection) -> str:
    return (
        f"{connection.src_component}.{connection.src_port}"
        f"->{connection.dst_component}.{connection.dst_port}"
    )
