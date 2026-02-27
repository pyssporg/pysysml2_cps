"""Inheritance resolution for SysML part definitions."""

from __future__ import annotations

import copy
from typing import Dict, List, Set, Tuple

from .definitions import (
    SysMLAttribute,
    SysMLConnection,
    SysMLPartDefinition,
    SysMLPartReference,
    SysMLPortReference,
)


def resolve_part_inheritance(parts: Dict[str, SysMLPartDefinition]) -> None:
    visited: Set[str] = set()
    visiting: Set[str] = set()
    stack: List[str] = []

    def resolve(name: str) -> None:
        if name in visited:
            return
        if name in visiting:
            start = stack.index(name)
            cycle = " -> ".join(stack[start:] + [name])
            raise ValueError(f"Inheritance cycle detected: {cycle}")

        visiting.add(name)
        stack.append(name)

        part = parts[name]
        if part.base_part_name is not None:
            if part.base_part_name not in parts:
                raise ValueError(
                    f"Base part definition not found for {part.name}: {part.base_part_name}"
                )
            part.base_part_def = parts[part.base_part_name]
            resolve(part.base_part_name)
            _merge_with_base(part, parts[part.base_part_name])

        stack.pop()
        visiting.remove(name)
        visited.add(name)

    for name in parts:
        resolve(name)


def _merge_with_base(part: SysMLPartDefinition, base: SysMLPartDefinition) -> None:
    merged_attributes = copy.deepcopy(base.attributes)
    merged_ports = copy.deepcopy(base.ports)
    merged_parts = copy.deepcopy(base.parts)
    merged_connections = copy.deepcopy(base.connections)

    for attr_name in part.remove_attributes:
        if attr_name not in merged_attributes:
            raise ValueError(f"Cannot remove unknown attribute {part.name}.{attr_name}")
        del merged_attributes[attr_name]
    for port_name in part.remove_ports:
        if port_name not in merged_ports:
            raise ValueError(f"Cannot remove unknown port {part.name}.{port_name}")
        del merged_ports[port_name]
    for part_name in part.remove_parts:
        if part_name not in merged_parts:
            raise ValueError(f"Cannot remove unknown part {part.name}.{part_name}")
        del merged_parts[part_name]
    for connection in part.remove_connections:
        if not _remove_connection(merged_connections, connection):
            raise ValueError(f"Cannot remove unknown connection in {part.name}: {connection}")

    _apply_redefines(
        part=part,
        merged_attributes=merged_attributes,
        merged_ports=merged_ports,
        merged_parts=merged_parts,
    )
    _apply_additions(
        part=part,
        merged_attributes=merged_attributes,
        merged_ports=merged_ports,
        merged_parts=merged_parts,
    )

    for connection in part.declared_connections:
        if _contains_connection(merged_connections, connection):
            raise ValueError(
                f"Connection already exists in {part.name}: "
                f"{connection.src_component}.{connection.src_port} to "
                f"{connection.dst_component}.{connection.dst_port} "
                f"(use remove connect first)"
            )
        merged_connections.append(connection)

    part.attributes = merged_attributes
    part.ports = merged_ports
    part.parts = merged_parts
    part.connections = merged_connections


def _apply_redefines(
    *,
    part: SysMLPartDefinition,
    merged_attributes: Dict[str, SysMLAttribute],
    merged_ports: Dict[str, SysMLPortReference],
    merged_parts: Dict[str, SysMLPartReference],
) -> None:
    for attr_name, attr in part.replace_attributes.items():
        if attr_name not in merged_attributes:
            raise ValueError(f"Cannot redefine unknown attribute {part.name}.{attr_name}")
        merged_attributes[attr_name] = attr
    for port_name, port in part.replace_ports.items():
        if port_name not in merged_ports:
            raise ValueError(f"Cannot redefine unknown port {part.name}.{port_name}")
        merged_ports[port_name] = port
    for part_name, subpart in part.replace_parts.items():
        if part_name not in merged_parts:
            raise ValueError(f"Cannot redefine unknown part {part.name}.{part_name}")
        merged_parts[part_name] = subpart


def _apply_additions(
    *,
    part: SysMLPartDefinition,
    merged_attributes: Dict[str, SysMLAttribute],
    merged_ports: Dict[str, SysMLPortReference],
    merged_parts: Dict[str, SysMLPartReference],
) -> None:
    for attr_name, attr in part.declared_attributes.items():
        if attr_name in merged_attributes:
            raise ValueError(
                f"Attribute name collision in {part.name}: {attr_name} (use redefines attribute)"
            )
        merged_attributes[attr_name] = attr
    for port_name, port in part.declared_ports.items():
        if port_name in merged_ports:
            raise ValueError(
                f"Port name collision in {part.name}: {port_name} (use redefines in/out port)"
            )
        merged_ports[port_name] = port
    for part_name, subpart in part.declared_parts.items():
        if part_name in merged_parts:
            raise ValueError(
                f"Part name collision in {part.name}: {part_name} (use redefines part)"
            )
        merged_parts[part_name] = subpart


def _connection_key(connection: SysMLConnection) -> Tuple[str, str, str, str]:
    return (
        connection.src_component,
        connection.src_port,
        connection.dst_component,
        connection.dst_port,
    )


def _remove_connection(
    target_connections: List[SysMLConnection], connection: SysMLConnection
) -> bool:
    key = _connection_key(connection)
    for idx, candidate in enumerate(target_connections):
        if _connection_key(candidate) == key:
            del target_connections[idx]
            return True
    return False


def _contains_connection(
    target_connections: List[SysMLConnection], connection: SysMLConnection
) -> bool:
    key = _connection_key(connection)
    return any(_connection_key(candidate) == key for candidate in target_connections)

