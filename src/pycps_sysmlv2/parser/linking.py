"""Reference-linking passes for parsed SysML objects."""

from __future__ import annotations

from typing import Dict

from ..definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
    SysMLRequirementReference,
    SysMLPartReference,
    SysMLPortReference,
    SysMLConnection
)
from ..definitions.base import NodeType


def attach_port_definitions(
    parts: Dict[str, SysMLPartDefinition], port_defs: Dict[str, SysMLPortDefinition]
) -> None:
    for part in parts.values():
        for port in part.refs(NodeType.Port).values():
            port: SysMLPortReference
            port.ref_node = port_defs.get(port.type)
            if port.ref_node is None:
                raise ValueError(
                    f"Port definition not found for {part.name}.{port.name}: {port.type}"
                )


def attach_part_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        for subpart in part.refs(NodeType.Part).values():
            subpart: SysMLPartReference
            subpart.ref_node = parts.get(subpart.type)


def attach_connection_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        part_map = part.refs(NodeType.Part)
        for connection in part.defs(NodeType.Connection).values():
            connection: SysMLConnection
            src_part = connection.src_part
            dst_part = connection.dst_part
            src_port = connection.src_port
            dst_port = connection.dst_port

            if src_part not in part_map:
                raise ValueError(
                    f"Subpart not found for connection: {part.name}.{src_part}"
                )
            if dst_part not in part_map:
                raise ValueError(
                    f"Subpart not found for connection: {part.name}.{dst_part}"
                )

            connection.src_part_node = part_map[src_part]
            connection.dst_part_node = part_map[dst_part]
            if connection.src_part_node.ref_node is None:
                raise ValueError(
                    f"Part definition not found for subpart {part.name}.{src_part}"
                )
            if connection.dst_part_node.ref_node is None:
                raise ValueError(
                    f"Part definition not found for subpart {part.name}.{dst_part}"
                )

            src_ports = connection.src_part_node.ref_node.refs(NodeType.Port)
            dst_ports = connection.dst_part_node.ref_node.refs(NodeType.Port)
            if src_port not in src_ports:
                raise ValueError(
                    f"Port not found for connection: {connection.src_part_node.ref_node.name}.{src_port}"
                )
            if dst_port not in dst_ports:
                raise ValueError(
                    f"Port not found for connection: {connection.dst_part_node.ref_node.name}.{dst_port}"
                )

            connection.src_port_node = src_ports[src_port]
            connection.dst_port_node = dst_ports[dst_port]
            if connection.src_port_node.ref_node is None:
                raise ValueError(
                    "Port definition not found for connection endpoint: "
                    f"{connection.src_part_node.ref_node.name}.{src_port}"
                )
            if connection.dst_port_node.ref_node is None:
                raise ValueError(
                    "Port definition not found for connection endpoint: "
                    f"{connection.dst_part_node.ref_node.name}.{dst_port}"
                )


def attach_requirement_definitions(
    parts: Dict[str, SysMLPartDefinition],
    ports: Dict[str, SysMLPortDefinition],
    requirement_defs: Dict[str, SysMLRequirementDefinition],
) -> None:
    for part in parts.values():
        for requirement in part.refs(NodeType.Requirement).values():
            requirement: SysMLRequirementReference
            requirement.ref_node = requirement_defs.get(requirement.type)
            if requirement.ref_node is None:
                raise ValueError(
                    "Requirement usage references unknown requirement definition "
                    f"{requirement.type} in part {part.name}"
                )

    for port in ports.values():
        for requirement in port.refs(NodeType.Requirement).values():
            requirement: SysMLRequirementReference
            requirement.ref_node = requirement_defs.get(requirement.type)
            if requirement.ref_node is None:
                raise ValueError(
                    "Requirement usage references unknown requirement definition "
                    f"{requirement.type} in port {port.name}"
                )
