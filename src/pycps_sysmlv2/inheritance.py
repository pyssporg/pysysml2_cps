"""Inheritance resolution for SysML part definitions."""

from __future__ import annotations

import copy
from typing import Dict, List, Set, Tuple

from .definitions import (
    SysMLConnection,
    SysMLPartDefinition,
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
        if part.specializes is not None:
            if part.specializes not in parts:
                raise ValueError(
                    f"Base part definition not found for {part.name}: {part.specializes}"
                )
            part.base_part_def = parts[part.specializes]
            part.base_part_name = part.specializes
            resolve(part.specializes)
            _merge_with_base(part, parts[part.specializes])

        stack.pop()
        visiting.remove(name)
        visited.add(name)

    for name in parts:
        resolve(name)


def _merge_with_base(part: SysMLPartDefinition, base: SysMLPartDefinition) -> None:
    merged_attributes = copy.deepcopy(base.items.get("attributes", {}))
    merged_ports = copy.deepcopy(base.items.get("ports", {}))
    merged_parts = copy.deepcopy(base.items.get("parts", {}))
    merged_connections = copy.deepcopy(getattr(base, "connections", []))

    merged_by_kind = {
        "attributes": merged_attributes,
        "ports": merged_ports,
        "parts": merged_parts,
    }
    for kind, merged in merged_by_kind.items():
        _apply_generic_remove(part=part, kind=kind, merged=merged)

    for connection in getattr(part, "remove_connections", []):
        if not _remove_connection(merged_connections, connection):
            raise ValueError(f"Cannot remove unknown connection in {part.name}: {connection}")

    for kind, merged in merged_by_kind.items():
        _apply_generic_redefines(part=part, kind=kind, merged=merged)
    for kind, merged in merged_by_kind.items():
        _apply_generic_additions(part=part, kind=kind, merged=merged)

    for connection in getattr(part, "declared_connections", []):
        if _contains_connection(merged_connections, connection):
            raise ValueError(
                f"Connection already exists in {part.name}: "
                f"{connection.src_component}.{connection.src_port} to "
                f"{connection.dst_component}.{connection.dst_port} "
                f"(use remove connect first)"
            )
        merged_connections.append(connection)

    part.items["attributes"] = merged_attributes
    part.items["ports"] = merged_ports
    part.items["parts"] = merged_parts
    part.items["connections"] = {
        f"{_connection_key(c)}#{idx}": c for idx, c in enumerate(merged_connections)
    }
    part.attributes = part.items["attributes"]
    part.ports = part.items["ports"]
    part.parts = part.items["parts"]
    part.connections = merged_connections


def _apply_generic_remove(
    *, part: SysMLPartDefinition, kind: str, merged: Dict[str, object]
) -> None:
    singular = kind[:-1]
    for key in part.remove_items.get(kind, set()):
        if key not in merged:
            raise ValueError(f"Cannot remove unknown {singular} {part.name}.{key}")
        del merged[key]


def _apply_generic_redefines(
    *, part: SysMLPartDefinition, kind: str, merged: Dict[str, object]
) -> None:
    singular = kind[:-1]
    for key, value in part.redefines_items.get(kind, {}).items():
        if key not in merged:
            raise ValueError(f"Cannot redefine unknown {singular} {part.name}.{key}")
        merged[key] = value


def _apply_generic_additions(
    *, part: SysMLPartDefinition, kind: str, merged: Dict[str, object]
) -> None:
    singular = kind[:-1]
    for key, value in part.items.get(kind, {}).items():
        if key in merged:
            hint = {
                "attributes": "redefines attribute",
                "ports": "redefines in/out port",
                "parts": "redefines part",
            }.get(kind, f"redefines {singular}")
            raise ValueError(
                f"{singular.capitalize()} name collision in {part.name}: {key} (use {hint})"
            )
        merged[key] = value


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
