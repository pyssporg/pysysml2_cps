from __future__ import annotations

from dataclasses import dataclass

from .base import InherenceDefinition, NodeType


@dataclass
class SysMLPartDefinition(InherenceDefinition):
    DEF_KINDS: tuple[NodeType, ...] = (
        NodeType.Attribute,
        NodeType.Part,
        NodeType.Port,
        NodeType.Requirement,
        NodeType.Connection,
    )
    REF_KINDS: tuple[NodeType, ...] = (
        NodeType.Part,
        NodeType.Port,
        NodeType.Requirement,
    )


