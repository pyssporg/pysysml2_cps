"""Traceability Preamble
Template ID: PYCSYSML2_TRACE_PREAMBLE
Template Version: 1.1.0
Purpose: Resolve inheritance links between parsed SysML definitions.
Design Notes:
- Apply inheritance after all definitions are loaded to ensure cross-file references resolve.
- Propagate inherited members while preserving locally declared overrides.
Key Invariants:
- Missing base types should raise explicit parser errors rather than silently skipping.
- Resolution order must avoid duplicating inherited members.
Strongly Connected External Modules:
- pycps_sysmlv2.definitions
- pycps_sysmlv2.parser.errors
Decision Log:
- Add dated, behavior-impacting decisions; avoid logging template-only edits.
"""
from __future__ import annotations

from typing import Dict, List, Set

from .definitions import (
    SysMLPartDefinition,
    SysMLPortDefinition,
    SysMLRequirementDefinition,
)
from .definitions.base import InherenceDefinition


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
            base_name = _specializes_name(definition.specializes)
            if base_name not in definitions:
                raise ValueError(
                    f"Base {label} definition not found for {definition.name}: {base_name}"
                )
            definition.specializes_obj = definitions[base_name]
            resolve(base_name)
            _validate_resolved_items(definition)

        stack.pop()
        visiting.remove(name)
        visited.add(name)

    for name in definitions:
        resolve(name)


def _validate_resolved_items(definition: InherenceDefinition) -> None:
    # Resolve both declared-def and declared-ref views so invalid remove/redefine
    # entries are raised during parsing.
    for kind in definition.DEF_KINDS:
        definition.defs(kind)
    for kind in definition.REF_KINDS:
        definition.refs(kind)


def _specializes_name(value: object) -> str:
    return getattr(value, "name", value)
