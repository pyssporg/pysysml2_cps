from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .attributes import SysMLAttribute
from .base import DefinitionBase
from .connections import SysMLConnection
from .references import SysMLPartReference, SysMLPortReference


@dataclass
class SysMLPortDefinition(DefinitionBase):
    name: str
    doc: Optional[str] = None
    attributes: Dict[str, SysMLAttribute] = field(default_factory=dict)
    source_file: Optional[str] = None


@dataclass
class SysMLPartDefinition(DefinitionBase):
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
