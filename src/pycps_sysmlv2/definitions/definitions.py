from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

from .base import DeclaredDefinition


@dataclass
class ResolvedRequirement(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("text",)

@dataclass
class SysMLRequirement(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("text",)

    @property
    def identifier(self) -> str:
        return self.name

    @identifier.setter
    def identifier(self, value: str) -> None:
        self.name = value

    @property
    def text(self) -> str:
        payload = self.items.setdefault("text", {}).setdefault("text", "")
        return str(payload)

    @text.setter
    def text(self, value: str) -> None:
        self.items.setdefault("text", {})["text"] = value


@dataclass
class ResolvedPortDefinition(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes",)

@dataclass
class SysMLPortDefinition(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes",)

    @property
    def attributes(self) -> Dict[str, object]:
        return self.items.setdefault("attributes", {})

    @attributes.setter
    def attributes(self, value: Dict[str, object]) -> None:
        self.items["attributes"] = value


@dataclass
class ResolvedPartDefinition(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes", "ports", "parts", "connections")

@dataclass
class SysMLPartDefinition(DeclaredDefinition):
    artifact_kinds: Tuple[str, ...] = ("attributes", "ports", "parts", "connections")

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
