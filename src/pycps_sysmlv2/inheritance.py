"""Inheritance resolution for SysML part definitions."""

from __future__ import annotations

import copy
from typing import Dict, List, Set

from .definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
    SysMLConnection,
    DefinitionBase,
    InherenceDefinition
)


def resolve_part_inheritance(parts: Dict[str, SysMLPartDefinition]) -> None:
    _resolve_definition_inheritance(parts, label="part")


def resolve_requirement_inheritance(
    requirements: Dict[str, SysMLRequirementDefinition],
) -> None:
    _resolve_definition_inheritance(requirements, label="requirement")


def resolve_port_inheritance(
    ports: Dict[str, SysMLPortDefinition],
) -> None:
    _resolve_definition_inheritance(ports, label="port")


def _resolve_definition_inheritance(definitions: Dict[str, InherenceDefinition], label: str) -> None:
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

        definition = definitions[name]
        if definition.specializes is not None:
            if definition.specializes not in definitions:
                raise ValueError(
                    f"Base {label} definition not found for {definition.name}: {definition.specializes}"
                )
            definition.specializes_obj = definitions[definition.specializes]
            resolve(definition.specializes)
            _merge_with_base(definition, definitions[definition.specializes])

        stack.pop()
        visiting.remove(name)
        visited.add(name)

    for name in definitions:
        resolve(name)


def _merge_with_base(definition: InherenceDefinition, base: InherenceDefinition) -> None:
    declared_items = getattr(definition, "declared_items", definition.refs)
    merged_by_kind = {
        kind: copy.deepcopy(base.refs.get(kind, {}))
        for kind in definition.reference_kinds
        if kind != "connections"
    }
    merged_connections = copy.deepcopy(base.refs.get("connections", {}))

    for kind, merged in merged_by_kind.items():
        _apply_generic_remove(definition=definition, kind=kind, merged=merged)

    for key in definition.remove_references.get("connections", set()):
        if key not in merged_connections:
            raise ValueError(f"Cannot remove unknown connection in {definition.name}: {key}")
        del merged_connections[key]

    for kind, merged in merged_by_kind.items():
        _apply_generic_redefines(definition=definition, kind=kind, merged=merged)
    for kind, merged in merged_by_kind.items():
        _apply_generic_additions(
            definition=definition,
            kind=kind,
            merged=merged,
            additions=declared_items.get(kind, {}),
        )

    for key, connection in declared_items.get("connections", {}).items():
        connection :SysMLConnection
        if key in merged_connections:
            raise ValueError(
                f"Connection already exists in {definition.name}: "
                f"{connection.src_component}.{connection.src_port} to "
                f"{connection.dst_component}.{connection.dst_port} "
                f"(use remove connect first)"
            )
        merged_connections[key] = connection

    for kind, merged in merged_by_kind.items():
        definition.refs[kind] = merged
    if "connections" in definition.reference_kinds:
        definition.refs["connections"] = merged_connections


def _apply_generic_remove(
    *, definition: InherenceDefinition, kind: str, merged: Dict[str, InherenceDefinition]
) -> None:
    singular = kind[:-1]
    for key in definition.remove_references.get(kind, set()):
        if key not in merged:
            raise ValueError(f"Cannot remove unknown {singular} {definition.name}.{key}")
        del merged[key]


def _apply_generic_redefines(
    *, definition: InherenceDefinition, kind: str, merged: Dict[str, InherenceDefinition]
) -> None:
    singular = kind[:-1]
    for key, value in definition.redefines_references.get(kind, {}).items():
        if key not in merged:
            raise ValueError(f"Cannot redefine unknown {singular} {definition.name}.{key}")
        merged[key] = value


def _apply_generic_additions(
    *,
    definition: InherenceDefinition,
    kind: str,
    merged: Dict[str, InherenceDefinition],
    additions: Dict[str, InherenceDefinition],
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
                f"{singular.capitalize()} name collision in {definition.name}: {key} (use {hint})"
            )
        merged[key] = value
