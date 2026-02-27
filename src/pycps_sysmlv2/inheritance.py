"""Inheritance resolution for SysML part definitions."""

from __future__ import annotations

import copy
from typing import Dict, List, Set

from .definitions import (
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
            part.specializes_obj = parts[part.specializes]
            resolve(part.specializes)
            _merge_with_base(part, parts[part.specializes])

        stack.pop()
        visiting.remove(name)
        visited.add(name)

    for name in parts:
        resolve(name)


def _merge_with_base(part: SysMLPartDefinition, base: SysMLPartDefinition) -> None:
    declared_items = getattr(part, "declared_items", part.items)
    merged_by_kind = {
        kind: copy.deepcopy(base.items.get(kind, {}))
        for kind in part.artifact_kinds
        if kind != "connections"
    }
    merged_connections = copy.deepcopy(base.items.get("connections", {}))

    for kind, merged in merged_by_kind.items():
        _apply_generic_remove(part=part, kind=kind, merged=merged)

    for key in part.remove_items.get("connections", set()):
        if key not in merged_connections:
            raise ValueError(f"Cannot remove unknown connection in {part.name}: {key}")
        del merged_connections[key]

    for kind, merged in merged_by_kind.items():
        _apply_generic_redefines(part=part, kind=kind, merged=merged)
    for kind, merged in merged_by_kind.items():
        _apply_generic_additions(
            part=part,
            kind=kind,
            merged=merged,
            additions=declared_items.get(kind, {}),
        )

    for key, connection in declared_items.get("connections", {}).items():
        if key in merged_connections:
            raise ValueError(
                f"Connection already exists in {part.name}: "
                f"{connection.src_component}.{connection.src_port} to "
                f"{connection.dst_component}.{connection.dst_port} "
                f"(use remove connect first)"
            )
        merged_connections[key] = connection

    for kind, merged in merged_by_kind.items():
        part.items[kind] = merged
    part.items["connections"] = merged_connections


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
    *,
    part: SysMLPartDefinition,
    kind: str,
    merged: Dict[str, object],
    additions: Dict[str, object],
) -> None:
    singular = kind[:-1]
    for key, value in additions.items():
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
