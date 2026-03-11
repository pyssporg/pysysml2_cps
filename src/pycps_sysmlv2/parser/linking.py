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


def attach_port_definitions(
    parts: Dict[str, SysMLPartDefinition], port_defs: Dict[str, SysMLPortDefinition]
) -> None:
    for part in parts.values():
        for port in part._refs.get("ports", {}).values():
            port: SysMLPortReference
            port.ref_node = port_defs.get(port.type)
            if port.ref_node is None:
                raise ValueError(
                    f"Port definition not found for {part.name}.{port.name}: {port.type}"
                )


def attach_part_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        for subpart in part._refs.get("parts", {}).values():
            subpart: SysMLPartReference
            subpart.ref_node = parts.get(subpart.type)


def attach_connection_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        part_map = part._refs.get("parts", {})
        for connection in part._refs.get("connections", {}).values():
            connection: SysMLConnection
            if connection.src_component not in part_map:
                raise ValueError(
                    f"Subpart not found for connection: {part.name}.{connection.src_component}"
                )
            if connection.dst_component not in part_map:
                raise ValueError(
                    f"Subpart not found for connection: {part.name}.{connection.dst_component}"
                )

            connection.src_part_def = part_map[connection.src_component].part_def
            connection.dst_part_def = part_map[connection.dst_component].part_def
            if connection.src_part_def is None:
                raise ValueError(
                    f"Part definition not found for subpart {part.name}.{connection.src_component}"
                )
            if connection.dst_part_def is None:
                raise ValueError(
                    f"Part definition not found for subpart {part.name}.{connection.dst_component}"
                )

            src_ports = connection.src_part_def.refs.get("ports", {})
            dst_ports = connection.dst_part_def.refs.get("ports", {})
            if connection.src_port not in src_ports:
                raise ValueError(
                    f"Port not found for connection: {connection.src_part_def.name}.{connection.src_port}"
                )
            if connection.dst_port not in dst_ports:
                raise ValueError(
                    f"Port not found for connection: {connection.dst_part_def.name}.{connection.dst_port}"
                )

            connection.src_port_def = src_ports[connection.src_port].port_def
            connection.dst_port_def = dst_ports[connection.dst_port].port_def
            if connection.src_port_def is None:
                raise ValueError(
                    "Port definition not found for connection endpoint: "
                    f"{connection.src_part_def.name}.{connection.src_port}"
                )
            if connection.dst_port_def is None:
                raise ValueError(
                    "Port definition not found for connection endpoint: "
                    f"{connection.dst_part_def.name}.{connection.dst_port}"
                )


def attach_requirement_definitions(
    parts: Dict[str, SysMLPartDefinition],
    ports: Dict[str, SysMLPortDefinition],
    requirement_defs: Dict[str, SysMLRequirementDefinition],
) -> None:
    for part in parts.values():
        for requirement in part._refs.get("requirements", {}).values():
            requirement: SysMLRequirementReference
            requirement.ref_node = requirement_defs.get(requirement.type)
            if requirement.ref_node is None:
                raise ValueError(
                    "Requirement usage references unknown requirement definition "
                    f"{requirement.type} in part {part.name}"
                )

    for port in ports.values():
        for requirement in port._refs.get("requirements", {}).values():
            requirement: SysMLRequirementReference
            requirement.ref_node = requirement_defs.get(requirement.type)
            if requirement.ref_node is None:
                raise ValueError(
                    "Requirement usage references unknown requirement definition "
                    f"{requirement.type} in port {port.name}"
                )
