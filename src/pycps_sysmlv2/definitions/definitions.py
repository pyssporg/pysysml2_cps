from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .base import DeclaredDefinition


@dataclass
class ResolvedRequirement(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("text",)

@dataclass
class SysMLRequirement(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("text",)


@dataclass
class ResolvedPortDefinition(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes",)

@dataclass
class SysMLPortDefinition(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes",)


@dataclass
class ResolvedPartDefinition(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes", "ports", "parts", "connections")

@dataclass
class SysMLPartDefinition(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes", "ports", "parts", "connections")

