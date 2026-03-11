from __future__ import annotations

from dataclasses import dataclass

from .base import InherenceDefinition, NodeType
from .attributes import SysMLAttribute


@dataclass
class SysMLRequirementDefinition(InherenceDefinition):
    DEF_KINDS: tuple[NodeType, ...] = (NodeType.Attribute,)
    REF_KINDS: tuple[NodeType, ...] = tuple()

    @property
    def text(self) -> str:
        value = self.get_def(NodeType.Attribute, "text").value
        return str(value)

    @text.setter
    def text(self, value) -> str:
        attrib = SysMLAttribute.from_literal(name="text", value=value, doc=None )
        self.add_def(NodeType.Attribute, "text", attrib)