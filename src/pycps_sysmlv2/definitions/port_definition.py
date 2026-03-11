from __future__ import annotations

from dataclasses import dataclass

from .base import InherenceDefinition, NodeType


@dataclass
class SysMLPortDefinition(InherenceDefinition):
    DEF_KINDS: tuple[NodeType, ...] = (NodeType.Attribute,)
    REF_KINDS: tuple[NodeType, ...] = tuple()

