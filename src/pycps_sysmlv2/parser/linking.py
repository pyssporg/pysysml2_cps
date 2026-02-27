"""Reference-linking passes for parsed SysML objects."""

from __future__ import annotations

from typing import Dict

from ..definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
)


def attach_port_definitions(
    parts: Dict[str, SysMLPartDefinition], port_defs: Dict[str, SysMLPortDefinition]
) -> None:
    for part in parts.values():
        for port in part.items.get("ports", {}).values():
            port.port_def = port_defs.get(port.port_name)
            if port.port_def is None:
                raise ValueError(
                    f"Port definition not found for {part.name}.{port.name}: {port.port_name}"
                )


def attach_part_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        for subpart in part.items.get("parts", {}).values():
            subpart.part_def = parts.get(subpart.part_name)


def attach_connection_definitions(parts: Dict[str, SysMLPartDefinition]) -> None:
    for part in parts.values():
        part_map = part.items.get("parts", {})
        for connection in part.items.get("connections", {}).values():
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

            src_ports = connection.src_part_def.items.get("ports", {})
            dst_ports = connection.dst_part_def.items.get("ports", {})
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
        for requirement in part.items.get("requirements", {}).values():
            requirement.requirement_def = requirement_defs.get(requirement.requirement_name)
            if requirement.requirement_def is None:
                raise ValueError(
                    "Requirement usage references unknown requirement definition "
                    f"{requirement.requirement_name} in part {part.name}"
                )

    for port in ports.values():
        for requirement in port.items.get("requirements", {}).values():
            requirement.requirement_def = requirement_defs.get(requirement.requirement_name)
            if requirement.requirement_def is None:
                raise ValueError(
                    "Requirement usage references unknown requirement definition "
                    f"{requirement.requirement_name} in port {port.name}"
                )
