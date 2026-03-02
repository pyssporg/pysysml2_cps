from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

from .base import InherenceDefinition
from .port_definition import SysMLPortDefinition
from .requirement_definition import SysMLRequirementDefinition


@dataclass
class SysMLPartDefinition(InherenceDefinition):
    artifact_kinds: Tuple[str, ...] = (
        "attributes",
        "ports",
        "parts",
        "connections",
        "requirements",
    )

    @property
    def attributes(self) -> Dict[str, object]:
        return self.items.setdefault("attributes", {})

    @attributes.setter
    def attributes(self, value: Dict[str, object]) -> None:
        self.items["attributes"] = value

    @property
    def ports(self) -> Dict[str, object]:
        return self.items.setdefault("ports", {})

    @ports.setter
    def ports(self, value: Dict[str, object]) -> None:
        self.items["ports"] = value

    @property
    def parts(self) -> Dict[str, object]:
        return self.items.setdefault("parts", {})

    @parts.setter
    def parts(self, value: Dict[str, object]) -> None:
        self.items["parts"] = value

    @property
    def connections(self) -> list[object]:
        return list(self.items.setdefault("connections", {}).values())

    @connections.setter
    def connections(self, value: Iterable[object] | Dict[str, object]) -> None:
        if isinstance(value, dict):
            self.items["connections"] = value
            return
        mapped: Dict[str, object] = {}
        for c in value:
            key = (
                f"{getattr(c, 'src_component')}.{getattr(c, 'src_port')}"
                f"->{getattr(c, 'dst_component')}.{getattr(c, 'dst_port')}"
            )
            mapped[key] = c
        self.items["connections"] = mapped

    def add_part(
        self,
        name: str,
        part_name: str,
        part_def: Optional["SysMLPartDefinition"] = None,
        doc: Optional[str] = None,
    ) -> "SysMLPartReference":
        from .references import SysMLPartReference

        part_ref = SysMLPartReference(
            name=name,
            part_name=part_name,
            part_def=part_def,
            doc=doc,
        )
        self.parts[name] = part_ref
        return part_ref

    def remove_part(self, name: str) -> "SysMLPartReference":
        if name not in self.parts:
            raise KeyError(f"Part reference not found: {name}")
        return self.parts.pop(name)  # type: ignore[return-value]

    def add_port(
        self,
        name: str,
        direction: str,
        port_name: str,
        port_def: Optional[SysMLPortDefinition] = None,
        doc: Optional[str] = None,
    ) -> "SysMLPortReference":
        from .references import SysMLPortReference

        port_ref = SysMLPortReference(
            name=name,
            direction=direction,
            port_name=port_name,
            port_def=port_def,
            doc=doc,
        )
        self.ports[name] = port_ref
        return port_ref

    def remove_port(self, name: str) -> "SysMLPortReference":
        if name not in self.ports:
            raise KeyError(f"Port reference not found: {name}")
        return self.ports.pop(name)  # type: ignore[return-value]

    def add_requirement(
        self,
        name: str,
        requirement_name: Optional[str] = None,
        requirement_def: Optional[SysMLRequirementDefinition] = None,
        doc: Optional[str] = None,
    ) -> "SysMLRequirementReference":
        from .references import SysMLRequirementReference

        resolved_name = requirement_name or (
            requirement_def.name if requirement_def is not None else name
        )
        requirement_ref = SysMLRequirementReference(
            name=name,
            requirement_name=resolved_name,
            requirement_def=requirement_def,
            doc=doc,
        )
        self.items.setdefault("requirements", {})[name] = requirement_ref
        return requirement_ref

    def remove_requirement(self, name: str) -> "SysMLRequirementReference":
        requirements = self.items.setdefault("requirements", {})
        if name not in requirements:
            raise KeyError(f"Requirement reference not found: {name}")
        return requirements.pop(name)  # type: ignore[return-value]

    def add_connection(
        self,
        src_component: str,
        src_port: str,
        dst_component: str,
        dst_port: str,
        *,
        src_part_def: Optional["SysMLPartDefinition"] = None,
        dst_part_def: Optional["SysMLPartDefinition"] = None,
        src_port_def: Optional[SysMLPortDefinition] = None,
        dst_port_def: Optional[SysMLPortDefinition] = None,
        name: str = "",
        doc: Optional[str] = None,
    ) -> "SysMLConnection":
        from .connections import SysMLConnection

        connection = SysMLConnection(
            name=name,
            src_component=src_component,
            src_port=src_port,
            dst_component=dst_component,
            dst_port=dst_port,
            src_part_def=src_part_def,
            dst_part_def=dst_part_def,
            src_port_def=src_port_def,
            dst_port_def=dst_port_def,
            doc=doc,
        )
        key = self._connection_key(src_component, src_port, dst_component, dst_port)
        self.items.setdefault("connections", {})[key] = connection
        return connection

    def remove_connection(
        self, src_component: str, src_port: str, dst_component: str, dst_port: str
    ) -> "SysMLConnection":
        key = self._connection_key(src_component, src_port, dst_component, dst_port)
        connections = self.items.setdefault("connections", {})
        if key not in connections:
            raise KeyError(f"Connection not found: {key}")
        return connections.pop(key)  # type: ignore[return-value]

    @staticmethod
    def _connection_key(
        src_component: str, src_port: str, dst_component: str, dst_port: str
    ) -> str:
        return f"{src_component}.{src_port}->{dst_component}.{dst_port}"
