from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .base import InherenceDefinition, DefinitionBase
from .attributes import SysMLAttribute
from .types import SysMLType


@dataclass
class SysMLRequirementDefinition(DefinitionBase):
    DEF_KINDS: tuple[str, ...] = ("attributes",)
    REF_KINDS: tuple[str, ...] = tuple()

    def add_attributes_def(self, key: str, reference: SysMLAttribute):
        self.add_def(kind="attributes", key=key, obj=reference)

    def remove_attributes_def(self, key: str):
        self.remove_def(kind="attributes", key=key)

    def get_attributes_def(self, key: str):
        return self.get_def(kind="attributes", key=key)

    def add_text(self, value: str):
        attrib = SysMLAttribute.from_literal(name="text", value=value)
        self.add_attributes_def("text", attrib)

    @property
    def text(self) -> str:
        value = self.get_def("attributes", "text").value
        return str(value)
